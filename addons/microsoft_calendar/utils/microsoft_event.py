#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectra.apiimportmodel
fromtypingimportIterator,Mapping
fromcollectionsimportabc
fromflectra.toolsimportReadonlyDict
fromflectra.addons.microsoft_calendar.utils.event_id_storageimportcombine_ids


classMicrosoftEvent(abc.Set):
    """
    ThishelperclassholdsthevaluesofaMicrosoftevent.
    InspiredbyFlectrarecordset,oneinstancecanbeasingleMicrosofteventora
    (immutable)setofMicrosoftevents.
    Allusualsetoperationsaresupported(union,intersection,etc).

    :paramiterable:iterableofMicrosoftCalendarinstancesoriterableofdictionnaries
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

    def__iter__(self)->Iterator['MicrosoftEvent']:
        returniter(MicrosoftEvent([vals])forvalsinself._events.values())

    def__contains__(self,microsoft_event):
        returnmicrosoft_event.idinself._events

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
        """
        Use'id'toreturnaneventidentifierwhichisspecifictoacalendar
        """
        returntuple(e.idforeinself)

    defmicrosoft_ids(self):
        returntuple(e.idforeinself)

    @property
    defuids(self):
        """
        Use'iCalUid'toreturnanidentifierwhichisuniqueaccrossallcalendars
        """
        returntuple(e.iCalUIdforeinself)

    defflectra_id(self,env):
        returnself._flectra_id

    def_meta_flectra_id(self,microsoft_guid):
        """ReturnstheFlectraidstoredintheMicrosoftEventmetadata.
        Thisidmightnotactuallyexistsinthedatabase.
        """
        returnNone

    @property
    defflectra_ids(self):
        """
        GetthelistofFlectraeventidsalreadymappedwithOutlookevents(self)
        """
        returntuple(e._flectra_idforeinselfife._flectra_id)

    def_load_flectra_ids_from_db(self,env,force_model=None):
        """
        MapMicrosofteventstoexistingFlectraevents:
        1)extractunmappedeventsonly,
        2)matchFlectraeventsandOutlookeventswhichhavebothaICalUIdset,
        3)matchremainingevents,
        Returnsthelistofmappedevents
        """
        mapped_events=[e.idforeinselfife._flectra_id]

        #avoidmappingeventsiftheyarealreadyallmapped
        iflen(self)==len(mapped_events):
            returnself

        unmapped_events=self.filter(lambdae:e.idnotinmapped_events)

        model_env=force_modelifforce_modelisnotNoneelseself._get_model(env)
        flectra_events=model_env.with_context(active_test=False).search([
            '|',
            ('ms_universal_event_id',"in",unmapped_events.uids),
            ('ms_organizer_event_id',"in",unmapped_events.ids)
        ]).with_env(env)

        #1.trytomatchunmappedeventswithFlectraeventsusingtheiriCalUId
        unmapped_events_with_uids=unmapped_events.filter(lambdae:e.iCalUId)
        flectra_events_with_uids=flectra_events.filtered(lambdae:e.ms_universal_event_id)
        mapping={e.ms_universal_event_id:e.idforeinflectra_events_with_uids}

        forms_eventinunmapped_events_with_uids:
            flectra_id=mapping.get(ms_event.iCalUId)
            ifflectra_id:
                ms_event._events[ms_event.id]['_flectra_id']=flectra_id
                mapped_events.append(ms_event.id)

        #2.trytomatchunmappedeventswithFlectraeventsusingtheirid
        unmapped_events=self.filter(lambdae:e.idnotinmapped_events)
        mapping={e.ms_organizer_event_id:eforeinflectra_events}

        forms_eventinunmapped_events:
            flectra_event=mapping.get(ms_event.id)
            ifflectra_event:
                ms_event._events[ms_event.id]['_flectra_id']=flectra_event.id
                mapped_events.append(ms_event.id)

                #don'tforgettoalsosettheglobaleventIDontheFlectraeventtoease
                #andimprovereliabilityoffuturemappings
                flectra_event.write({
                    'microsoft_id':combine_ids(ms_event.id,ms_event.iCalUId),
                    'need_sync_m':False,
                })

        returnself.filter(lambdae:e.idinmapped_events)

    defowner_id(self,env):
        """
        Indicateswhoistheownerofanevent(i.etheorganizeroftheevent).

        Thereareseveralpossiblecases:
        1)thecurrentFlectrauseristheorganizeroftheeventaccordingtoOutlookevent,soreturnhisid.
        2)thecurrentFlectrauserisNOTtheorganizerand:
           2.1)weareabletofindaFlectrauserusingtheOutlookeventorganizeremailaddressandweusehisid,
           2.2)weareNOTabletofindaFlectrausermatchingtheorganizeremailaddressandwereturnFalse,meaning
                thatnoFlectrauserwillbeabletomodifythisevent.AllmodificationswillbedonefromOutlook.
        """
        ifself.isOrganizer:
            returnenv.user.id
        ifself.organizer.get('emailAddress')andself.organizer.get('emailAddress').get('address'):
            #Warning:InMicrosoft:1email=1user;butinFlectraseveralusersmighthavethesameemail
            user=env['res.users'].search([('email','=',self.organizer.get('emailAddress').get('address'))],limit=1)
            returnuser.idifuserelseFalse
        returnFalse

    deffilter(self,func)->'MicrosoftEvent':
        returnMicrosoftEvent(eforeinselfiffunc(e))

    defis_recurrence(self):
        returnself.type=='seriesMaster'

    defis_recurrent(self):
        returnbool(self.seriesMasterIdorself.is_recurrence())

    defis_recurrent_not_master(self):
        returnbool(self.seriesMasterId)

    defget_recurrence(self):
        ifnotself.recurrence:
            return{}
        pattern=self.recurrence['pattern']
        range=self.recurrence['range']
        end_type_dict={
            'endDate':'end_date',
            'noEnd':'forever',
            'numbered':'count',
        }
        type_dict={
            'absoluteMonthly':'monthly',
            'relativeMonthly':'monthly',
            'absoluteYearly':'yearly',
            'relativeYearly':'yearly',
        }
        index_dict={
            'first':'1',
            'second':'2',
            'third':'3',
            'fourth':'4',
            'last':'-1',
        }
        rrule_type=type_dict.get(pattern['type'],pattern['type'])
        interval=pattern['interval']
        ifrrule_type=='yearly':
            interval*=12
        result={
            'rrule_type':rrule_type,
            'end_type':end_type_dict.get(range['type'],False),
            'interval':interval,
            'count':range['numberOfOccurrences'],
            'day':pattern['dayOfMonth'],
            'byday':index_dict.get(pattern['index'],False),
            'until':range['type']=='endDate'andrange['endDate'],
        }

        month_by_dict={
            'absoluteMonthly':'date',
            'relativeMonthly':'day',
            'absoluteYearly':'date',
            'relativeYearly':'day',
        }
        month_by=month_by_dict.get(pattern['type'],False)
        ifmonth_by:
            result['month_by']=month_by

        #daysOfWeekcontainsthefullnameoftheday,thefieldscontainthefirst2letters(mo,tu,etc)
        week_days=[x[:2]forxinpattern.get('daysOfWeek',[])]
        forweek_dayin['mo','tu','we','th','fr','sa','su']:
            result[week_day]=week_dayinweek_days
        ifweek_days:
            result['weekday']=week_days[0].upper()
        returnresult

    defis_cancelled(self):
        returnbool(self.isCancelled)orself.is_removed()

    defis_removed(self):
        returnself.__getattr__('@removed')andself.__getattr__('@removed').get('reason')=='deleted'

    defis_recurrence_outlier(self):
        returnself.type=="exception"

    defcancelled(self):
        returnself.filter(lambdae:e.is_cancelled())

    defmatch_with_flectra_events(self,env)->'MicrosoftEvent':
        """
        MatchOutlookevents(self)withexistingFlectraevents,andreturnthelistofmatchedevents
        """
        #first,trytomatchrecurrences
        #Notethatwhenarecurrenceisremoved,thereisnofieldinOutlookdatatoidentify
        #theitemasarecurrence,soselectalldeleteditemsbydefault.
        recurrence_candidates=self.filter(lambdax:x.is_recurrence()orx.is_removed())
        mapped_recurrences=recurrence_candidates._load_flectra_ids_from_db(env,force_model=env["calendar.recurrence"])

        #then,trytomatchevents
        events_candidates=(self-mapped_recurrences).filter(lambdax:notx.is_recurrence())
        mapped_events=events_candidates._load_flectra_ids_from_db(env)

        returnmapped_recurrences|mapped_events

    def_get_model(self,env):
        ifall(e.is_recurrence()foreinself):
            returnenv['calendar.recurrence']
        ifall(note.is_recurrence()foreinself):
            returnenv['calendar.event']
        raiseTypeError("MixingMicrosofteventsandMicrosoftrecurrences")
