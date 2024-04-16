flectra.define('mail.Many2OneAvatarUser',function(require){
    "usestrict";

    //ThismoduledefinesanextensionoftheMany2OneAvatarwidget,whichis
    //integratedwiththemessagingsystem.TheMany2OneAvatarUserisdesigned
    //todisplaypeople,andwhentheavatarofthosepeopleisclicked,it
    //opensaDMchatwindowwiththecorrespondinguser.
    //
    //Thiswidgetissupportedonmany2onefieldspointingto'res.users'.
    //
    //Usage:
    //  <fieldname="user_id"widget="many2one_avatar_user"/>
    //
    //Thewidgetisdesignedtobeextended,tosupportmany2onefieldspointing
    //toothermodelsthan'res.users'.

    constfieldRegistry=require('web.field_registry');
    const{Many2OneAvatar}=require('web.relational_fields');

    const{Component}=owl;

    constMany2OneAvatarUser=Many2OneAvatar.extend({
        events:Object.assign({},Many2OneAvatar.prototype.events,{
            'click.o_m2o_avatar':'_onAvatarClicked',
        }),
        //Thiswidgetisonlysupportedonmany2onespointingto'res.users'
        supportedModels:['res.users'],

        init(){
            this._super(...arguments);
            if(!this.supportedModels.includes(this.field.relation)){
                thrownewError(`Thiswidgetisonlysupportedonmany2onefieldspointingto${JSON.stringify(this.supportedModels)}`);
            }
            if(this.mode==='readonly'){
                this.className+='o_clickable_m2o_avatar';
            }
        },

        //----------------------------------------------------------------------
        //Handlers
        //----------------------------------------------------------------------

        /**
         *Whentheavatarisclicked,openaDMchatwindowwiththe
         *correspondinguser.
         *
         *@private
         *@param{MouseEvent}ev
         */
        async_onAvatarClicked(ev){
            ev.stopPropagation();//inlistview,preventfromopeningtherecord
            constenv=Component.env;
            awaitenv.messaging.openChat({userId:this.value.res_id});
        }
    });

    constKanbanMany2OneAvatarUser=Many2OneAvatarUser.extend({
        _template:'mail.KanbanMany2OneAvatarUser',
    });

    fieldRegistry.add('many2one_avatar_user',Many2OneAvatarUser);
    fieldRegistry.add('kanban.many2one_avatar_user',KanbanMany2OneAvatarUser);

    return{
        Many2OneAvatarUser,
        KanbanMany2OneAvatarUser,
    };
});
