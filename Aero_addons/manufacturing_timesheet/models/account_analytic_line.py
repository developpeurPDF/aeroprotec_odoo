# -*- coding: utf-8 -*-
################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Cybrosys Technologies(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from collections import defaultdict
import json

from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_round, format_datetime


class AccountAnalyticLine(models.Model):
    """Inherited model account_analytic_line to add a new field related
       to manufacturing timesheet."""
    _inherit = 'account.analytic.line'

    is_manufacturing = fields.Boolean(string='Est-ce que la fabrication', invisible=True,
                                      help='Ce booléen aidera à reconnaître la feuille de temps liée à la fabrication.')

    unit_amount = fields.Float(
        'Quantité',
        default=0.0, inverse='_set_duration'
    )

    def _set_duration(self):

        def _float_duration_to_second(unit_amount):
            minutes = unit_amount // 1
            seconds = (unit_amount % 1) * 60
            return minutes * 60 + seconds

        for order in self:
            old_order_duration = sum(order.time_ids.mapped('duration'))
            new_order_duration = order.duration
            if new_order_duration == old_order_duration:
                continue

            delta_duration = new_order_duration - old_order_duration

            if delta_duration > 0:
                enddate = datetime.now()
                date_start = enddate - timedelta(seconds=_float_duration_to_second(delta_duration))
                if order.duration_expected >= new_order_duration or old_order_duration >= order.duration_expected:
                    # either only productive or only performance (i.e. reduced speed) time respectively
                    self.env['mrp.workcenter.productivity'].create(
                        order._prepare_timeline_vals(new_order_duration, date_start, enddate)
                    )
                else:
                    # split between productive and performance (i.e. reduced speed) times
                    maxdate = fields.Datetime.from_string(enddate) - relativedelta(minutes=new_order_duration - order.duration_expected)
                    self.env['mrp.workcenter.productivity'].create([
                        order._prepare_timeline_vals(order.duration_expected, date_start, maxdate),
                        order._prepare_timeline_vals(new_order_duration, maxdate, enddate)
                    ])
            else:
                duration_to_remove = abs(delta_duration)
                timelines_to_unlink = self.env['mrp.workcenter.productivity']
                for timeline in order.time_ids.sorted():
                    if duration_to_remove <= 0.0:
                        break
                    if timeline.duration <= duration_to_remove:
                        duration_to_remove -= timeline.duration
                        timelines_to_unlink |= timeline
                    else:
                        new_time_line_duration = timeline.duration - duration_to_remove
                        timeline.date_start = timeline.date_end - timedelta(seconds=_float_duration_to_second(new_time_line_duration))
                        break
                timelines_to_unlink.unlink()