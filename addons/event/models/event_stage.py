#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimport_,fields,models


classEventStage(models.Model):
    _name='event.stage'
    _description='EventStage'
    _order='sequence,name'

    name=fields.Char(string='StageName',required=True,translate=True)
    description=fields.Text(string='Stagedescription',translate=True)
    sequence=fields.Integer('Sequence',default=1)
    fold=fields.Boolean(string='FoldedinKanban',default=False)
    pipe_end=fields.Boolean(
        string='EndStage',default=False,
        help='Eventswillautomaticallybemovedintothisstagewhentheyarefinished.Theeventmovedintothisstagewillautomaticallybesetasgreen.')
    legend_blocked=fields.Char(
        'RedKanbanLabel',default=lambdas:_('Blocked'),translate=True,required=True,
        help='Overridethedefaultvaluedisplayedfortheblockedstateforkanbanselection.')
    legend_done=fields.Char(
        'GreenKanbanLabel',default=lambdas:_('ReadyforNextStage'),translate=True,required=True,
        help='Overridethedefaultvaluedisplayedforthedonestateforkanbanselection.')
    legend_normal=fields.Char(
        'GreyKanbanLabel',default=lambdas:_('InProgress'),translate=True,required=True,
        help='Overridethedefaultvaluedisplayedforthenormalstateforkanbanselection.')
