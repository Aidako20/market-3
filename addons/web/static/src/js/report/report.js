flectra.define('report',function(require){
'usestrict';

require('web.dom_ready');
varutils=require('report.utils');

if(window.self===window.top){
    return;
}

$(document.body)
    .addClass('o_in_iframe')
    .addClass('container-fluid')
    .removeClass('container');

varweb_base_url=window.origin;
vartrusted_host=utils.get_host_from_url(web_base_url);
vartrusted_protocol=utils.get_protocol_from_url(web_base_url);
vartrusted_origin=utils.build_origin(trusted_protocol,trusted_host);

//Allowsendingcommandstothewebclient
//`do_action`command
$('[res-id][res-model][view-type]')
    .wrap('<a/>')
    .attr('href','#')
    .on('click',function(ev){
        ev.preventDefault();
        varaction={
            'type':'ir.actions.act_window',
            'view_mode':$(this).attr('view-mode')||$(this).attr('view-type'),
            'res_id':Number($(this).attr('res-id')),
            'res_model':$(this).attr('res-model'),
            'views':[
                [$(this).attr('view-id')||false,$(this).attr('view-type')],
            ],
        };
        window.parent.postMessage({
            'message':'report:do_action',
            'action':action,
        },trusted_origin);
    });
});
