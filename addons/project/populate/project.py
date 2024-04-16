#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importlogging
importcollections

fromflectraimportmodels
fromflectra.toolsimportpopulate

_logger=logging.getLogger(__name__)

classProjectStage(models.Model):
    _inherit="project.task.type"
    _populate_sizes={"small":10,"medium":50,"large":500}

    def_populate_factories(self):
        return[
            ("name",populate.constant('stage_{counter}')),
            ("sequence",populate.randomize([False]+[iforiinrange(1,101)])),
            ("description",populate.constant('project_stage_description_{counter}')),
            ("active",populate.randomize([True,False],[0.8,0.2])),
            ("fold",populate.randomize([True,False],[0.9,0.1]))
        ]

classProjectProject(models.Model):
    _inherit="project.project"
    _populate_sizes={"small":10,"medium":50,"large":1000}
    _populate_dependencies=["res.company","project.task.type"]

    def_populate_factories(self):
        company_ids=self.env.registry.populated_models["res.company"]
        stage_ids=self.env.registry.populated_models["project.task.type"]

        defget_company_id(random,**kwargs):
            returnrandom.choice(company_ids)
            #user_idsfromcompany.user_ids?
            #Alsoaddapartner_idsonres_company?

        defget_stage_ids(random,**kwargs):
            return[
                (6,0,[
                    random.choice(stage_ids)
                    foriinrange(random.choice([jforjinrange(1,10)]))
                ])
            ]

        return[
            ("name",populate.constant('project_{counter}')),
            ("sequence",populate.randomize([False]+[iforiinrange(1,101)])),
            ("active",populate.randomize([True,False],[0.8,0.2])),
            ("company_id",populate.compute(get_company_id)),
            ("type_ids",populate.compute(get_stage_ids)),
            ('color',populate.randomize([False]+[iforiinrange(1,7)])),
            #TODOuser_idbutwhataboutmulti-companycoherence??
        ]


classProjectTask(models.Model):
    _inherit="project.task"
    _populate_sizes={"small":500,"medium":5000,"large":50000}
    _populate_dependencies=["project.project"]

    def_populate_factories(self):
        project_ids=self.env.registry.populated_models["project.project"]
        stage_ids=self.env.registry.populated_models["project.task.type"]
        defget_project_id(random,**kwargs):
            returnrandom.choice([False,False,False]+project_ids)
        defget_stage_id(random,**kwargs):
            returnrandom.choice([False,False]+stage_ids)
        return[
            ("name",populate.constant('project_task_{counter}')),
            ("sequence",populate.randomize([False]+[iforiinrange(1,101)])),
            ("active",populate.randomize([True,False],[0.8,0.2])),
            ("color",populate.randomize([False]+[iforiinrange(1,7)])),
            ("kanban_state",populate.randomize(['normal','done','blocked'])),
            ("project_id",populate.compute(get_project_id)),
            ("stage_id",populate.compute(get_stage_id)),
        ]

    def_populate(self,size):
        records=super()._populate(size)
        #setparent_ids
        self._populate_set_children_tasks(records,size)
        returnrecords

    def_populate_set_children_tasks(self,tasks,size):
        _logger.info('Settingparenttasks')
        rand=populate.Random('project.task+children_generator')
        parents=self.env["project.task"]
        fortaskintasks:
            ifnotrand.getrandbits(4):
                parents|=task
        parent_ids=parents.ids
        tasks-=parents
        parent_childs=collections.defaultdict(lambda:self.env['project.task'])
        forcount,taskinenumerate(tasks):
            ifnotrand.getrandbits(4):
                parent_childs[rand.choice(parent_ids)]|=task

        forcount,(parent,childs)inenumerate(parent_childs.items()):
            if(count+1)%100==0:
                _logger.info('Settingparent:%s/%s',count+1,len(parent_childs))
            childs.write({'parent_id':parent})
