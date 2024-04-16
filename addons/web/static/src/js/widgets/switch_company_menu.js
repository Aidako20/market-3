flectra.define('web.SwitchCompanyMenu',function(require){
"usestrict";

/**
 *WhenFlectraisconfiguredinmulti-companymode,usersshouldobviouslybeable
 *toswitchtheirinterfacefromonecompanytotheother. Thisisthepurpose
 *ofthiswidget,bydisplayingadropdownmenuinthesystray.
 */

varconfig=require('web.config');
varcore=require('web.core');
varsession=require('web.session');
varSystrayMenu=require('web.SystrayMenu');
varWidget=require('web.Widget');

var_t=core._t;

varSwitchCompanyMenu=Widget.extend({
    template:'SwitchCompanyMenu',
    events:{
        'click.dropdown-item[data-menu]div.log_into':'_onSwitchCompanyClick',
        'keydown.dropdown-item[data-menu]div.log_into':'_onSwitchCompanyClick',
        'click.dropdown-item[data-menu]div.toggle_company':'_onToggleCompanyClick',
        'keydown.dropdown-item[data-menu]div.toggle_company':'_onToggleCompanyClick',
    },
    //forcethisitemtobethefirstonetotheleftoftheUserMenuinthesystray
    sequence:1,
    /**
     *@override
     */
    init:function(){
        this._super.apply(this,arguments);
        this.isMobile=config.device.isMobile;
        this._onSwitchCompanyClick=_.debounce(this._onSwitchCompanyClick,1500,true);
    },

    /**
     *@override
     */
    willStart:function(){
        varself=this;
        this.allowed_company_ids=String(session.user_context.allowed_company_ids)
                                    .split(',')
                                    .map(function(id){returnparseInt(id);});
        this.user_companies=session.user_companies.allowed_companies;
        this.current_company=this.allowed_company_ids[0];
        this.current_company_name=_.find(session.user_companies.allowed_companies,function(company){
            returncompany[0]===self.current_company;
        })[1];
        returnthis._super.apply(this,arguments);
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     *@param{MouseEvent|KeyEvent}ev
     */
    _onSwitchCompanyClick:function(ev){
        if(ev.type=='keydown'&&ev.which!=$.ui.keyCode.ENTER&&ev.which!=$.ui.keyCode.SPACE){
            return;
        }
        ev.preventDefault();
        ev.stopPropagation();
        vardropdownItem=$(ev.currentTarget).parent();
        vardropdownMenu=dropdownItem.parent();
        varcompanyID=dropdownItem.data('company-id');
        varallowed_company_ids=this.allowed_company_ids;
        if(dropdownItem.find('.fa-square-o').length){
            //1enabledcompany:Stayinsinglecompanymode
            if(this.allowed_company_ids.length===1){
                if(this.isMobile){
                    dropdownMenu=dropdownMenu.parent();
                }
                dropdownMenu.find('.fa-check-square').removeClass('fa-check-square').addClass('fa-square-o');
                dropdownItem.find('.fa-square-o').removeClass('fa-square-o').addClass('fa-check-square');
                allowed_company_ids=[companyID];
            }else{//Multicompanymode
                allowed_company_ids.push(companyID);
                dropdownItem.find('.fa-square-o').removeClass('fa-square-o').addClass('fa-check-square');
            }
        }
        $(ev.currentTarget).attr('aria-pressed','true');
        session.setCompanies(companyID,allowed_company_ids);
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     *@param{MouseEvent|KeyEvent}ev
     */
    _onToggleCompanyClick:function(ev){
        if(ev.type=='keydown'&&ev.which!=$.ui.keyCode.ENTER&&ev.which!=$.ui.keyCode.SPACE){
            return;
        }
        ev.preventDefault();
        ev.stopPropagation();
        vardropdownItem=$(ev.currentTarget).parent();
        varcompanyID=dropdownItem.data('company-id');
        varallowed_company_ids=this.allowed_company_ids;
        varcurrent_company_id=allowed_company_ids[0];
        if(dropdownItem.find('.fa-square-o').length){
            allowed_company_ids.push(companyID);
            dropdownItem.find('.fa-square-o').removeClass('fa-square-o').addClass('fa-check-square');
            $(ev.currentTarget).attr('aria-checked','true');
        }else{
            allowed_company_ids.splice(allowed_company_ids.indexOf(companyID),1);
            dropdownItem.find('.fa-check-square').addClass('fa-square-o').removeClass('fa-check-square');
            $(ev.currentTarget).attr('aria-checked','false');
        }
        session.setCompanies(current_company_id,allowed_company_ids);
    },

});

if(session.display_switch_company_menu){
    SystrayMenu.Items.push(SwitchCompanyMenu);
}

returnSwitchCompanyMenu;

});
