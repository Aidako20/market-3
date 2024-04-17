# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.
from flectra import models
from flectra.http import request


class IrHttp(models.AbstractModel):
_inherit = 'ir.http'

@classmethod
def _dispatch(cls):
affiliate_id = request.httprequest.args.get('affiliate_id')
if affiliate_id:
request.session['affiliate_id'] = int(affiliate_id)
return super(IrHttp, cls)._dispatch()
