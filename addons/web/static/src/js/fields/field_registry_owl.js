flectra.define('web.field_registry_owl',function(require){
    "usestrict";

    constRegistry=require('web.Registry');

    returnnewRegistry(
        null,
        (value)=>value.prototypeinstanceofowl.Component
    );
});

flectra.define('web._field_registry_owl',function(require){
    "usestrict";

    /**
     *Thismoduleregistersfieldcomponents(specificationsoftheAbstractFieldComponent)
     */

    constbasicFields=require('web.basic_fields_owl');
    constregistry=require('web.field_registry_owl');

    //Basicfields
    registry
        .add('badge',basicFields.FieldBadge)
        .add('boolean',basicFields.FieldBoolean);
});
