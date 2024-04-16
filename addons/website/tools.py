#-*-encoding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importcontextlib
importre
fromunittest.mockimportMock,MagicMock,patch

importwerkzeug

importflectra
fromflectra.tools.miscimportDotDict


defget_video_embed_code(video_url):
    '''ComputesthevalidiframefromgivenURLthatcanbeembedded
        (orFalseincaseofinvalidURL).
    '''

    ifnotvideo_url:
        returnFalse

    #TodetectifwehaveavalidURLornot
    validURLRegex=r'^(http:\/\/|https:\/\/|\/\/)[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$'

    #Regexforfewofthewidelyusedvideohostingservices
    ytRegex=r'^(?:(?:https?:)?\/\/)?(?:www\.)?(?:youtu\.be\/|youtube(-nocookie)?\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=))((?:\w|-){11})(?:\S+)?$'
    vimeoRegex=r'\/\/(player.)?vimeo.com\/([a-z]*\/)*([0-9]{6,11})[?]?.*'
    dmRegex=r'.+dailymotion.com\/(video|hub|embed)\/([^_?]+)[^#]*(#video=([^_&]+))?'
    igRegex=r'(.*)instagram.com\/p\/(.[a-zA-Z0-9]*)'
    ykuRegex=r'(.*).youku\.com\/(v_show\/id_|embed\/)(.+)'

    ifnotre.search(validURLRegex,video_url):
        returnFalse
    else:
        embedUrl=False
        ytMatch=re.search(ytRegex,video_url)
        vimeoMatch=re.search(vimeoRegex,video_url)
        dmMatch=re.search(dmRegex,video_url)
        igMatch=re.search(igRegex,video_url)
        ykuMatch=re.search(ykuRegex,video_url)

        ifytMatchandlen(ytMatch.groups()[1])==11:
            embedUrl='//www.youtube%s.com/embed/%s?rel=0'%(ytMatch.groups()[0]or'',ytMatch.groups()[1])
        elifvimeoMatch:
            embedUrl='//player.vimeo.com/video/%s'%(vimeoMatch.groups()[2])
        elifdmMatch:
            embedUrl='//www.dailymotion.com/embed/video/%s'%(dmMatch.groups()[1])
        elifigMatch:
            embedUrl='//www.instagram.com/p/%s/embed/'%(igMatch.groups()[1])
        elifykuMatch:
            ykuLink=ykuMatch.groups()[2]
            if'.html?'inykuLink:
                ykuLink=ykuLink.split('.html?')[0]
            embedUrl='//player.youku.com/embed/%s'%(ykuLink)
        else:
            #WedirectlyusetheprovidedURLasitis
            embedUrl=video_url
        return'<iframeclass="embed-responsive-item"src="%s"allowFullScreen="true"frameborder="0"></iframe>'%embedUrl


defwerkzeugRaiseNotFound(*args,**kwargs):
    raisewerkzeug.exceptions.NotFound()


@contextlib.contextmanager
defMockRequest(
        env,*,routing=True,multilang=True,
        context=None,
        cookies=None,country_code=None,website=None,sale_order_id=None
):
    router=MagicMock()
    match=router.return_value.bind.return_value.match
    ifrouting:
        match.return_value[0].routing={
            'type':'http',
            'website':True,
            'multilang':multilang
        }
    else:
        match.side_effect=werkzeugRaiseNotFound

    ifcontextisNone:
        context={}
    lang_code=context.get('lang',env.context.get('lang','en_US'))
    context.setdefault('lang',lang_code)

    request=Mock(
        context=context,
        db=None,
        endpoint=match.return_value[0]ifroutingelseNone,
        env=env,
        httprequest=Mock(
            host='localhost',
            path='/hello',
            app=flectra.http.root,
            environ={'REMOTE_ADDR':'127.0.0.1'},
            cookies=cookiesor{},
            referrer='',
        ),
        lang=env['res.lang']._lang_get(lang_code),
        redirect=werkzeug.utils.redirect,
        session=DotDict(
            geoip={'country_code':country_code},
            debug=False,
            sale_order_id=sale_order_id,
        ),
        website=website,
        render=lambda*a,**kw:'<MockResponse>',
    )

    withcontextlib.ExitStack()ass:
        flectra.http._request_stack.push(request)
        s.callback(flectra.http._request_stack.pop)
        s.enter_context(patch('flectra.http.root.get_db_router',router))

        yieldrequest
