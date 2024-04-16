flectra.define('hr.Many2OneAvatarEmployee',function(require){
    "usestrict";

    //ThismoduledefinesavariantoftheMany2OneAvatarUserfieldwidget,
    //tosupportmany2onefieldspointingto'hr.employee'.Italsodefinesthe
    //kanbanversionofthiswidget.
    //
    //Usage:
    //  <fieldname="employee_id"widget="many2one_avatar_employee"/>

    constfieldRegistry=require('web.field_registry');
    const{Many2OneAvatarUser,KanbanMany2OneAvatarUser}=require('mail.Many2OneAvatarUser');

    const{Component}=owl;

    constMany2OneAvatarEmployeeMixin={
        supportedModels:['hr.employee','hr.employee.public'],

        //----------------------------------------------------------------------
        //Private
        //----------------------------------------------------------------------

        /**
         *@override
         */
        async_onAvatarClicked(ev){
            ev.stopPropagation();//inlistview,preventfromopeningtherecord
            constenv=Component.env;
            awaitenv.messaging.openChat({employeeId:this.value.res_id});
        }
    };

    constMany2OneAvatarEmployee=Many2OneAvatarUser.extend(Many2OneAvatarEmployeeMixin);
    constKanbanMany2OneAvatarEmployee=KanbanMany2OneAvatarUser.extend(Many2OneAvatarEmployeeMixin);

    fieldRegistry.add('many2one_avatar_employee',Many2OneAvatarEmployee);
    fieldRegistry.add('kanban.many2one_avatar_employee',KanbanMany2OneAvatarEmployee);

    return{
        Many2OneAvatarEmployee,
        KanbanMany2OneAvatarEmployee,
    };
});
