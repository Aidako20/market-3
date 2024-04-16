#-*-coding:utf-8-*-
importast
importbase64
importlogging
importlxml
importos
importsys
importtempfile
importzipfile
fromcollectionsimportdefaultdict
fromos.pathimportjoinasopj

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError
fromflectra.modules.moduleimportMANIFEST_NAMES
fromflectra.toolsimportconvert_csv_import,convert_sql_import,convert_xml_import,exception_to_unicode
fromflectra.toolsimportfile_open,file_open_temporary_directory

_logger=logging.getLogger(__name__)

MAX_FILE_SIZE=100*1024*1024 #inmegabytes


classIrModule(models.Model):
    _inherit="ir.module.module"

    imported=fields.Boolean(string="ImportedModule")

    def_get_modules_to_load_domain(self):
        #importedmodulesarenotexpectedtobeloadedasregularmodules
        returnsuper()._get_modules_to_load_domain()+[('imported','=',False)]

    @api.depends('name')
    def_get_latest_version(self):
        imported_modules=self.filtered(lambdam:m.importedandm.latest_version)
        formoduleinimported_modules:
            module.installed_version=module.latest_version
        super(IrModule,self-imported_modules)._get_latest_version()

    def_import_module(self,module,path,force=False):
        known_mods=self.search([])
        known_mods_names={m.name:mforminknown_mods}
        installed_mods=[m.nameforminknown_modsifm.state=='installed']

        terp={}
        manifest_path=next((opj(path,name)fornameinMANIFEST_NAMESifos.path.exists(opj(path,name))),None)
        ifmanifest_path:
            withfile_open(manifest_path,'rb',env=self.env)asf:
                terp.update(ast.literal_eval(f.read().decode()))
        ifnotterp:
            returnFalse
        ifnotterp.get('icon'):
            icon_path='static/description/icon.png'
            module_icon=moduleifos.path.exists(opj(path,icon_path))else'base'
            terp['icon']=opj('/',module_icon,icon_path)
        values=self.get_values_from_terp(terp)
        if'version'interp:
            values['latest_version']=terp['version']

        unmet_dependencies=set(terp.get('depends',[])).difference(installed_mods)

        ifunmet_dependencies:
            if(unmet_dependencies==set(['web_studio'])and
                    _is_studio_custom(path)):
                err=_("StudiocustomizationsrequireStudio")
            else:
                err=_("Unmetmoduledependencies:\n\n-%s")%'\n-'.join(
                    known_mods.filtered(lambdamod:mod.nameinunmet_dependencies).mapped('shortdesc')
                )
            raiseUserError(err)
        elif'web_studio'notininstalled_modsand_is_studio_custom(path):
            raiseUserError(_("StudiocustomizationsrequiretheFlectraStudioapp."))

        mod=known_mods_names.get(module)
        ifmod:
            mod.write(dict(state='installed',**values))
            mode='update'ifnotforceelse'init'
        else:
            assertterp.get('installable',True),"Modulenotinstallable"
            self.create(dict(name=module,state='installed',imported=True,**values))
            mode='init'

        forkindin['data','init_xml','update_xml']:
            forfilenameinterp.get(kind,[]):
                ext=os.path.splitext(filename)[1].lower()
                ifextnotin('.xml','.csv','.sql'):
                    _logger.info("module%s:skipunsupportedfile%s",module,filename)
                    continue
                _logger.info("module%s:loading%s",module,filename)
                noupdate=False
                ifext=='.csv'andkindin('init','init_xml'):
                    noupdate=True
                pathname=opj(path,filename)
                idref={}
                withfile_open(pathname,'rb',env=self.env)asfp:
                    ifext=='.csv':
                        convert_csv_import(self.env.cr,module,pathname,fp.read(),idref,mode,noupdate)
                    elifext=='.sql':
                        convert_sql_import(self.env.cr,fp)
                    elifext=='.xml':
                        convert_xml_import(self.env.cr,module,fp,idref,mode,noupdate)

        path_static=opj(path,'static')
        IrAttachment=self.env['ir.attachment']
        ifos.path.isdir(path_static):
            forroot,dirs,filesinos.walk(path_static):
                forstatic_fileinfiles:
                    full_path=opj(root,static_file)
                    withfile_open(full_path,'rb',env=self.env)asfp:
                        data=base64.b64encode(fp.read())
                    url_path='/{}{}'.format(module,full_path.split(path)[1].replace(os.path.sep,'/'))
                    ifnotisinstance(url_path,str):
                        url_path=url_path.decode(sys.getfilesystemencoding())
                    filename=os.path.split(url_path)[1]
                    values=dict(
                        name=filename,
                        url=url_path,
                        res_model='ir.ui.view',
                        type='binary',
                        datas=data,
                    )
                    attachment=IrAttachment.search([('url','=',url_path),('type','=','binary'),('res_model','=','ir.ui.view')])
                    ifattachment:
                        attachment.write(values)
                    else:
                        IrAttachment.create(values)

        returnTrue

    @api.model
    defimport_zipfile(self,module_file,force=False):
        ifnotmodule_file:
            raiseException(_("Nofilesent."))
        ifnotzipfile.is_zipfile(module_file):
            raiseUserError(_('Onlyzipfilesaresupported.'))

        success=[]
        errors=dict()
        module_names=[]
        withzipfile.ZipFile(module_file,"r")asz:
            forzfinz.filelist:
                ifzf.file_size>MAX_FILE_SIZE:
                    raiseUserError(_("File'%s'exceedmaximumallowedfilesize",zf.filename))

            withfile_open_temporary_directory(self.env)asmodule_dir:
                manifest_files=[
                    file
                    forfileinz.filelist
                    iffile.filename.count('/')==1
                    andfile.filename.split('/')[1]inMANIFEST_NAMES
                ]
                module_data_files=defaultdict(list)
                formanifestinmanifest_files:
                    manifest_path=z.extract(manifest,module_dir)
                    mod_name=manifest.filename.split('/')[0]
                    try:
                        withfile_open(manifest_path,'rb',env=self.env)asf:
                            terp=ast.literal_eval(f.read().decode())
                    exceptException:
                        continue
                    forfilenameinterp.get('data',[])+terp.get('init_xml',[])+terp.get('update_xml',[]):
                        ifos.path.splitext(filename)[1].lower()notin('.xml','.csv','.sql'):
                            continue
                        module_data_files[mod_name].append('%s/%s'%(mod_name,filename))
                forfileinz.filelist:
                    filename=file.filename
                    mod_name=filename.split('/')[0]
                    is_data_file=filenameinmodule_data_files[mod_name]
                    is_static=filename.startswith('%s/static'%mod_name)
                    ifis_data_fileoris_static:
                        z.extract(file,module_dir)

                dirs=[dfordinos.listdir(module_dir)ifos.path.isdir(opj(module_dir,d))]
                formod_nameindirs:
                    module_names.append(mod_name)
                    try:
                        #assertmod_name.startswith('theme_')
                        path=opj(module_dir,mod_name)
                        ifself._import_module(mod_name,path,force=force):
                            success.append(mod_name)
                    exceptExceptionase:
                        _logger.exception('Errorwhileimportingmodule')
                        errors[mod_name]=exception_to_unicode(e)
        r=["Successfullyimportedmodule'%s'"%modformodinsuccess]
        formod,errorinerrors.items():
            r.append("Errorwhileimportingmodule'%s'.\n\n%s\nMakesurethosemodulesareinstalledandtryagain."%(mod,error))
        return'\n'.join(r),module_names

    defmodule_uninstall(self):
        #Deleteanir_module_modulerecordcompletelyifitwasanimported
        #one.Therationalebehindthisisthatanimportedmodule*cannot*be
        #reinstalledanyway,asitrequiresthedatafiles.Anyattemptto
        #installitagainwillsimplyfailwithouttrace.
        #/!\modules_to_deletemustbecalculatedbeforecallingsuper().module_uninstall(),
        #becausewhenuninstalling`base_import_module`the`imported`columnwillnolongerbe
        #inthedatabasebutwe'llstillhaveanoldregistrythatrunsthiscode.
        modules_to_delete=self.filtered('imported')
        res=super().module_uninstall()
        ifmodules_to_delete:
            _logger.info("deletingimportedmodulesuponuninstallation:%s",
                         ",".join(modules_to_delete.mapped('name')))
            modules_to_delete.unlink()
        returnres


def_is_studio_custom(path):
    """
    Checkstheto-be-importedrecordstoseeifthereareanyreferencesto
    studio,whichwouldmeanthatthemodulewascreatedusingstudio

    ReturnsTrueifanyoftherecordscontainsacontextwiththekey
    studioinit,Falseifnoneoftherecordsdo
    """
    filepaths=[]
    forlevelinos.walk(path):
        filepaths+=[os.path.join(level[0],fn)forfninlevel[2]]
    filepaths=[fpforfpinfilepathsiffp.lower().endswith('.xml')]

    forfpinfilepaths:
        root=lxml.etree.parse(fp).getroot()

        forrecordinroot:
            #theremightnotbeacontextifit'sanon-studiomodule
            try:
                #ast.literal_evalislikeeval(),butsafer
                #contextisastringrepresentingapythondict
                ctx=ast.literal_eval(record.get('context'))
                #therearenocasesinwhichstudioisfalse
                #sojustcheckingforitsexistenceisenough
                ifctxandctx.get('studio'):
                    returnTrue
            exceptException:
                continue
    returnFalse
