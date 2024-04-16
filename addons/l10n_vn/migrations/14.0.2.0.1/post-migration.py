#-*-coding:utf-8-*-
fromflectraimportapi,SUPERUSER_ID

FIXED_ACCOUNTS_MAP={
    '5221':'5211',
    '5222':'5212',
    '5223':'5213'
    }


def_fix_revenue_deduction_accounts_code(env):
    vn_template=env.ref('l10n_vn.vn_template')
    forcompanyinenv['res.company'].with_context(active_test=False).search([('chart_template_id','=',vn_template.id)]):
        forincorrect_code,correct_codeinFIXED_ACCOUNTS_MAP.items():
            account=env['account.account'].search([('code','=',incorrect_code),('company_id','=',company.id)])
            ifaccount:
                account.write({'code':correct_code})


defmigrate(cr,version):
    env=api.Environment(cr,SUPERUSER_ID,{})
    _fix_revenue_deduction_accounts_code(env)

