#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging
importtime

importlxml.html
fromwerkzeugimporturls

importflectra
importre

fromflectra.addons.base.tests.commonimportHttpCaseWithUserDemo

_logger=logging.getLogger(__name__)


@flectra.tests.common.tagged('post_install','-at_install','crawl')
classCrawler(HttpCaseWithUserDemo):
    """TestsuitecrawlinganFlectraCMSinstanceandcheckingthatall
    internallinksleadtoa200response.

    Ifausernameandapasswordareprovided,authenticatestheuserbefore
    startingthecrawl
    """

    defsetUp(self):
        super(Crawler,self).setUp()

        ifhasattr(self.env['res.partner'],'grade_id'):
            #Createatleastonepublishedparter,sothat/partnersdoesn't
            #returna404
            grade=self.env['res.partner.grade'].create({
                'name':'Atestgrade',
                'website_published':True,
            })
            self.env['res.partner'].create({
                'name':'ACompanyfor/partners',
                'is_company':True,
                'grade_id':grade.id,
                'website_published':True,
            })

    defcrawl(self,url,seen=None,msg=''):
        ifseenisNone:
            seen=set()

        url_slug=re.sub(r"[/](([^/=?&]+-)?[0-9]+)([/]|$)",'/<slug>/',url)
        url_slug=re.sub(r"([^/=?&]+)=[^/=?&]+",'\g<1>=param',url_slug)
        ifurl_sluginseen:
            returnseen
        else:
            seen.add(url_slug)

        _logger.info("%s%s",msg,url)
        r=self.url_open(url,allow_redirects=False)
        ifr.status_codein(301,302):
            #checklocalredirecttoavoidfetchexternalspages
            new_url=r.headers.get('Location')
            current_url=r.url
            ifurls.url_parse(new_url).netloc!=urls.url_parse(current_url).netloc:
                returnseen
            r=self.url_open(new_url)

        code=r.status_code
        self.assertIn(code,range(200,300),"%sFetching%sreturnederrorresponse(%d)"%(msg,url,code))

        ifr.headers['Content-Type'].startswith('text/html'):
            doc=lxml.html.fromstring(r.content)
            forlinkindoc.xpath('//a[@href]'):
                href=link.get('href')

                parts=urls.url_parse(href)
                #hrefwithanyfragmentremoved
                href=parts.replace(fragment='').to_url()

                #FIXME:handlerelativelink(notparts.path.startswith/)
                ifparts.netlocor\
                    notparts.path.startswith('/')or\
                    parts.path=='/web'or\
                    parts.path.startswith('/web/')or\
                    parts.path.startswith('/en_US/')or\
                    (parts.schemeandparts.schemenotin('http','https')):
                    continue

                self.crawl(href,seen,msg)
        returnseen

    deftest_10_crawl_public(self):
        t0=time.time()
        t0_sql=self.registry.test_cr.sql_log_count
        seen=self.crawl('/',msg='AnonymousCoward')
        count=len(seen)
        duration=time.time()-t0
        sql=self.registry.test_cr.sql_log_count-t0_sql
        _logger.runbot("publiccrawled%surlsin%.2fs%squeries,%.3fs%.2fqperrequest,",count,duration,sql,duration/count,float(sql)/count)

    deftest_20_crawl_demo(self):
        t0=time.time()
        t0_sql=self.registry.test_cr.sql_log_count
        self.authenticate('demo','demo')
        seen=self.crawl('/',msg='demo')
        count=len(seen)
        duration=time.time()-t0
        sql=self.registry.test_cr.sql_log_count-t0_sql
        _logger.runbot("democrawled%surlsin%.2fs%squeries,%.3fs%.2fqperrequest",count,duration,sql,duration/count,float(sql)/count)

    deftest_30_crawl_admin(self):
        t0=time.time()
        t0_sql=self.registry.test_cr.sql_log_count
        self.authenticate('admin','admin')
        seen=self.crawl('/',msg='admin')
        count=len(seen)
        duration=time.time()-t0
        sql=self.registry.test_cr.sql_log_count-t0_sql
        _logger.runbot("admincrawled%surlsin%.2fs%squeries,%.3fs%.2fqperrequest",count,duration,sql,duration/count,float(sql)/count)
