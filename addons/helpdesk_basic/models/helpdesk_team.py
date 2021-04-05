# Part of flectra. See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models, _
from flectra.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from datetime import datetime, timedelta
from babel.dates import format_datetime, format_date
import json
import ast


class HelpdeskTeam(models.Model):
    _name = 'helpdesk.team'
    _inherit = ['mail.thread', 'rating.parent.mixin', 'mail.alias.mixin']
    _description = 'Helpdesk Team'

    name = fields.Char('Helpdesk Team', required=True, translate=True)
    color = fields.Integer('Color Index', default=1)
    active = fields.Boolean(default=True)
    description = fields.Text('About Team', translate=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    sequence = fields.Integer("Sequence", default=10)
    member_ids = fields.Many2many('res.users', string='Members')
    alias_id = fields.Many2one('mail.alias', 'Alias', ondelete='restrict')
    issue_type_ids = fields.Many2many('issue.type', string='Issue Type')
    helpdesk_count = fields.Integer(compute='_compute_helpdesk_count',
                                    string='Total Helpdesk')
    stage_ids = fields.Many2many('helpdesk.stage', string='Stages')
    kanban_dashboard_graph = fields.Text(
        compute='_compute_kanban_dashboard_graph')

    def _determine_stage(self):
        """ Get a dict with the stage (per team) that should be set as first to a created ticket
            :returns a mapping of team identifier with the stage (maybe an empty record).
            :rtype : dict (key=team_id, value=record of helpdesk.stage)
        """
        result = dict.fromkeys(self.ids, self.env['helpdesk.stage'])
        for team in self:
            result[team.id] = self.env['helpdesk.stage'].search([('team_ids', 'in', team.id)], order='sequence', limit=1)
        return result

    def _determine_user_id(self):
        """ Get a dict with the user (per team) that should be assign to the nearly created ticket according to the team policy
            :returns a mapping of team identifier with the "to assign" user (maybe an empty record).
            :rtype : dict (key=team_id, value=record of res.users)
        """
        result = dict.fromkeys(self.ids, self.env['res.users'])
        for team in self:
            member_ids = sorted(team.member_ids.ids) if team.member_ids else sorted(team.visibility_member_ids.ids)
            if member_ids:
                if team.assignment_method == 'random':  # randomly means new tickets get uniformly distributed
                    last_assigned_user = self.env['helpdesk.ticket'].search([('team_id', '=', team.id)], order='create_date desc, id desc', limit=1).user_id
                    index = 0
                    if last_assigned_user and last_assigned_user.id in member_ids:
                        previous_index = member_ids.index(last_assigned_user.id)
                        index = (previous_index + 1) % len(member_ids)
                    result[team.id] = self.env['res.users'].browse(member_ids[index])
                elif team.assignment_method == 'balanced':  # find the member with the least open ticket
                    ticket_count_data = self.env['helpdesk.ticket'].read_group([('stage_id.is_close', '=', False), ('user_id', 'in', member_ids), ('team_id', '=', team.id)], ['user_id'], ['user_id'])
                    open_ticket_per_user_map = dict.fromkeys(member_ids, 0)  # dict: user_id -> open ticket count
                    open_ticket_per_user_map.update((item['user_id'][0], item['user_id_count']) for item in ticket_count_data)
                    result[team.id] = self.env['res.users'].browse(min(open_ticket_per_user_map, key=open_ticket_per_user_map.get))
        return result

    @api.model
    def _default_create_mail(self):
        return self.env.ref('helpdesk_basic.ticket_mail_template').id

    @api.model
    def _default_confirm_mail(self):
        return self.env.ref('helpdesk_basic.ticket_confirm_mail_template').id

    mail_template_id = fields.Many2one('mail.template', string="Create Mail Template", required=True, default=_default_create_mail)
    mail_close_tmpl_id = fields.Many2one('mail.template', string="Confirm Mail Template", default=_default_confirm_mail)
    assignment_method = fields.Selection([('manually', 'Manually'),
                                        ('random', 'Random'),
                                        ('balanced', 'Balanced')],
                                        string="Assignment Method", default='random')

    visibility_member_ids = fields.Many2many('res.users', 'users_members_info', string="Team Visibility")
    is_rating = fields.Boolean('Ratings On Tickets')
    
    def _compute_helpdesk_count(self):
        for team in self:
            team.helpdesk_count = self.env['helpdesk.ticket'].search_count([
                ('team_id', '=', team.id)])

    def write(self, vals):
        result = super(HelpdeskTeam, self).write(vals)
        if 'alias_name' in vals:
            for team in self:
                alias_vals = team._alias_get_creation_values()
        return result

    # ------------------------------------------------------------
    # MESSAGING
    # ------------------------------------------------------------

    def _alias_get_creation_values(self):
        values = super(HelpdeskTeam, self)._alias_get_creation_values()
        values['alias_model_id'] = self.env['ir.model']._get('helpdesk.ticket').id
        if self.id:
            values['alias_defaults'] = defaults = ast.literal_eval(self.alias_defaults or "{}")
            defaults['team_id'] = self.id
        return values

    def _compute_kanban_dashboard_graph(self):
        for record in self:
            record.kanban_dashboard_graph = json.dumps(
                record.get_bar_graph_datas())

    def get_bar_graph_datas(self):
        data = []
        today = datetime.strptime(str(fields.Date.context_today(self)), DF)
        data.append({'label': _('Past'), 'value': 0.0, 'type': 'past'})
        day_of_week = int(format_datetime(today, 'e', locale=self._context.get(
            'lang') or 'en_US'))
        first_day_of_week = today + timedelta(days=-day_of_week + 1)
        for i in range(-1, 4):
            if i == 0:
                label = _('This Week')
            elif i == 3:
                label = _('Future')
            else:
                start_week = first_day_of_week + timedelta(days=i * 7)
                end_week = start_week + timedelta(days=6)
                if start_week.month == end_week.month:
                    label = \
                        str(start_week.day) + '-' + str(end_week.day) + ' ' + \
                        format_date(end_week, 'MMM', locale=self._context.get(
                            'lang') or 'en_US')
                else:
                    label = \
                        format_date(start_week, 'd MMM',
                                    locale=self._context.get('lang') or 'en_US'
                                    ) + '-' + format_date(
                            end_week, 'd MMM',
                            locale=self._context.get('lang') or'en_US')
            data.append(
                {'label': label,
                 'value': 0.0,
                 'type': 'past' if i < 0 else 'future'})

        select_sql_clause = 'SELECT count(*) FROM helpdesk_ticket AS h ' \
                            'WHERE team_id = %(team_id)s'
        query_args = {'team_id': self.id}
        query = ''
        start_date = (first_day_of_week + timedelta(days=-7))
        for i in range(0, 6):
            if i == 0:
                query += "(" + select_sql_clause + " and start_date < '" + \
                         start_date.strftime(DF) + "')"
            elif i == 5:
                query += " UNION ALL (" + select_sql_clause + \
                         " and start_date >= '" + \
                         start_date.strftime(DF) + "')"
            else:
                next_date = start_date + timedelta(days=7)
                query += " UNION ALL (" + select_sql_clause + \
                         " and start_date >= '" + start_date.strftime(DF) + \
                         "' and start_date < '" + next_date.strftime(DF) + \
                         "')"
                start_date = next_date
        self.env.cr.execute(query, query_args)
        query_results = self.env.cr.dictfetchall()
        for index in range(0, len(query_results)):
            if query_results[index]:
                data[index]['value'] = query_results[index].get('count')
        return [{'values': data}]
