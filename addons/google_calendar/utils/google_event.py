#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectra.apiimportmodel
fromflectra.tools.miscimportReadonlyDict
fromflectra.tools.sqlimportexisting_tables
importpytz
importlogging
fromtypingimportIterator,Mapping
fromcollectionsimportabc
fromdateutil.parserimportparse
fromdateutil.relativedeltaimportrelativedelta


fromflectraimport_

_logger=logging.getLogger(__name__)


classGoogleEvent(abc.Set):
    """ThishelperclassholdsthevaluesofaGoogleevent.
    InspiredbyFlectrarecordset,oneinstancecanbeasingleGoogleeventora
    (immutable)setofGoogleevents.
    Allusualsetoperationsaresupported(union,intersection,etc).

    AlistofallattributescanbefoundintheAPIdocumentation.
    https://developers.google.com/calendar/v3/reference/events#resource

    :paramiterable:iterableofGoogleCalendarinstancesoriterableofdictionnaries

    """

    def__init__(self,iterable=()):
        _events={}
        foriteminiterable:
            ifisinstance(item,self.__class__):
                _events[item.id]=item._events[item.id]
            elifisinstance(item,Mapping):
                _events[item.get('id')]=item
            else:
                raiseValueError("Only%soriterableofdictaresupported"%self.__class__.__name__)
        self._events=ReadonlyDict(_events)

    def__iter__(self)-> Iterator['GoogleEvent']:
        returniter(GoogleEvent([vals])forvalsinself._events.values())

    def__contains__(self,google_event):
        returngoogle_event.idinself._events

    def__len__(self):
        returnlen(self._events)

    def__bool__(self):
        returnbool(self._events)

    def__getattr__(self,name):
        #ensure_one
        try:
            event,=self._events.keys()
        exceptValueError:
            raiseValueError("Expectedsingleton:%s"%self)
        event_id=list(self._events.keys())[0]
        returnself._events[event_id].get(name)

    def__repr__(self):
        return'%s%s'%(self.__class__.__name__,self.ids)

    @property
    defids(self):
        returntuple(e.idforeinself)

    @property
    defrrule(self):
        ifself.recurrenceandany('RRULE'initemforiteminself.recurrence):
            rrule=next(itemforiteminself.recurrenceif'RRULE'initem)
            returnrrule[6:] #skip"RRULE:"intherrulestring

    defflectra_id(self,env):
        self.flectra_ids(env) #loadids
        returnself._flectra_id

    def_meta_flectra_id(self,dbname):
        """ReturnstheFlectraidstoredintheGoogleEventmetadata.
        Thisidmightnotactuallyexistsinthedatabase.
        """
        properties=self.extendedPropertiesand(self.extendedProperties.get('shared',{})orself.extendedProperties.get('private',{}))or{}
        o_id=properties.get('%s_flectra_id'%dbname)
        ifo_id:
            returnint(o_id)

    defflectra_ids(self,env):
        ids=tuple(e._flectra_idforeinselfife._flectra_id)
        iflen(ids)==len(self):
            returnids
        model=self._get_model(env)
        found=self._load_flectra_ids_from_db(env,model)
        unsure=self-found
        ifunsure:
            unsure._load_flectra_ids_from_metadata(env,model)

        returntuple(e._flectra_idforeinself)

    def_load_flectra_ids_from_metadata(self,env,model):
        unsure_flectra_ids=tuple(e._meta_flectra_id(env.cr.dbname)foreinself)
        flectra_events=model.browse(_idfor_idinunsure_flectra_idsif_id)

        #ExtendedpropertiesarecopiedwhensplittingarecurrenceGoogleside.
        #Hence,wemayhavetwoGooglerecurrenceslinkedtothesameFlectraid.
        #Therefore,weonlyconsiderFlectrarecordswithoutgoogleidwhentrying
        #tomatchevents.
        o_ids=flectra_events.exists().filtered(lambdae:note.google_id).ids
        foreinself:
            flectra_id=e._meta_flectra_id(env.cr.dbname)
            ifflectra_idino_ids:
                e._events[e.id]['_flectra_id']=flectra_id

    def_load_flectra_ids_from_db(self,env,model):
        flectra_events=model.with_context(active_test=False)._from_google_ids(self.ids)
        mapping={e.google_id:e.idforeinflectra_events} #{google_id:flectra_id}
        existing_google_ids=flectra_events.mapped('google_id')
        foreinself:
            flectra_id=mapping.get(e.id)
            ifflectra_id:
                e._events[e.id]['_flectra_id']=flectra_id
        returnself.filter(lambdae:e.idinexisting_google_ids)


    defowner(self,env):
        #Owner/organizercouldbedesynchronisedbetweenGoogleandFlectra.
        #LetuserA,userBbetwonewusers(neversyncedtoGooglebefore).
        #UserAcreatesaneventinFlectra(heistheowner)butuserBsyncsfirst.
        #ThereisnowaytoinserttheeventintouserA'scalendarsincewedon'thave
        #anyauthenticationaccess.TheeventisthereforeinsertedintouserB'scalendar
        #(heistheorganizerinGoogle).The"real"owner(inFlectra)isstoredasan
        #extendedproperty.Thereiscurrentlynosupportto"transfert"ownershipwhen
        #userAsyncshiscalendarthefirsttime.
        real_owner_id=self.extendedPropertiesandself.extendedProperties.get('shared',{}).get('%s_owner_id'%env.cr.dbname)
        try:
            #Ifwecreateaneventwithoutuser_id,theeventpropertieswillbe'false'
            #andpythonwillinterpretthisaaNoneType,that'swhywehavethe'exceptTypeError'
            real_owner_id=int(real_owner_id)
        except(ValueError,TypeError):
            real_owner_id=False
        real_owner=real_owner_idandenv['res.users'].browse(real_owner_id)orenv['res.users']
        ifreal_owner_idandreal_owner.exists():
            returnreal_owner
        elifself.organizerandself.organizer.get('self'):
            returnenv.user
        elifself.organizerandself.organizer.get('email'):
            #InGoogle:1email=1user;butinFlectraseveralusersmighthavethesameemail:/
            returnenv['res.users'].search([('email','=',self.organizer.get('email'))],limit=1)
        else:
            returnenv['res.users']

    deffilter(self,func)->'GoogleEvent':
        returnGoogleEvent(eforeinselfiffunc(e))

    defclear_type_ambiguity(self,env):
        ambiguous_events=self.filter(GoogleEvent._is_type_ambiguous)
        recurrences=ambiguous_events._load_flectra_ids_from_db(env,env['calendar.recurrence'])
        forrecurrenceinrecurrences:
            self._events[recurrence.id]['recurrence']=True
        foreventinambiguous_events-recurrences:
            self._events[event.id]['recurrence']=False

    defis_recurrence(self):
        ifself._is_type_ambiguous():
            _logger.warning("Ambiguouseventtype:cannotaccuratelytellwhetheracancelledeventisarecurrenceornot")
        returnbool(self.recurrence)

    defis_recurrent(self):
        returnbool(self.recurringEventIdorself.is_recurrence())

    defis_cancelled(self):
        returnself.status=='cancelled'

    defis_recurrence_outlier(self):
        returnbool(self.originalStartTime)

    defcancelled(self):
        returnself.filter(lambdae:e.status=='cancelled')

    defexists(self,env)->'GoogleEvent':
        recurrences=self.filter(GoogleEvent.is_recurrence)
        events=self-recurrences
        recurrences.flectra_ids(env)
        events.flectra_ids(env)

        returnself.filter(lambdae:e._flectra_id)

    def_is_type_ambiguous(self):
        """Forcancelledevents/recurrences,Googleonlysendtheidand
        thecancelledstatus.Thereisnowaytoknowifitwasarecurrence
        orsimpleevent."""
        returnself.is_cancelled()and'recurrence'notinself._events[self.id]

    def_get_model(self,env):
        ifall(e.is_recurrence()foreinself):
            returnenv['calendar.recurrence']
        ifall(note.is_recurrence()foreinself):
            returnenv['calendar.event']
        raiseTypeError("MixingGoogleeventsandGooglerecurrences")
