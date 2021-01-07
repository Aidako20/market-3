/* Copyright 2016, 2019 Openworx.
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */

// Check if debug mode is active and then add debug into URL when clicking on the App sidebar
flectra.define('web_flectra.sidebar', function(require) {
    "use strict";
    var core = require('web.core');
    var config = require('web.config');
    var rpc = require('web.rpc');
    var session = require('web.session');

    var WebClient = require('web.WebClient');

    WebClient.include({
        start : function(){
            var self = this;
            this._super();
            return rpc.query({
                    model: 'res.company', method: 'read',
                    args: [[session.company_id], ['theme_menu_style']]
                }).then(function (res) {
                    if(res[0].theme_menu_style == 'sidemenu') {
                        $('.o-menu-toggle, .o_menu_sections').remove();
                }
            });
        },
    });

    $(document).ready(function(){
        $('.cssmenu > h3').click(function() {
            $('.cssmenu h3').removeClass('active');
            $("li.active").removeClass('active');
            $('.cssmenu .oe_menu_toggler').removeClass('active');
            $(this).closest('h3').addClass('active');
            var checkElement = $(this).next();
            if((checkElement.is('.oe_secondary_menu')) && (checkElement.is(':visible'))) {
                $(this).closest('h3').removeClass('active');
                checkElement.slideUp(400);
            }
            if((checkElement.is('.oe_secondary_menu')) && (!checkElement.is(':visible'))) {
                $('.cssmenu .oe_secondary_menu').slideUp(10);
                $('#cssmenu h3:visible').slideUp(400);
                checkElement.slideDown(400);
                var cssmenu = $(this).parent();
                $('.f_sub_menu_content').animate({ scrollTop: $(cssmenu).position().top - 46}, 500);
            }
        });

        $('.cssmenu .oe_menu_toggler').click(function(ev) {
            $('.cssmenu .oe_menu_toggler').removeClass('active');
            $(this).closest('.oe_menu_toggler').addClass('active');
            var checkElement = $(this).next();
            if((checkElement.is('.oe_secondary_submenu')) && (checkElement.is(':visible'))) {
                $(this).closest('.oe_menu_toggler').removeClass('active');
                checkElement.slideUp(400);
            }
            if((checkElement.is('.oe_secondary_submenu')) && (!checkElement.is(':visible'))) {
                $('#cssmenu .oe_menu_toggler:visible').slideUp(400);
                checkElement.slideDown(400);
            }
            return false;
        });

        $('.f_sub_menu_content').find('.oe_menu_toggler').siblings('.oe_secondary_submenu').hide();

        $('.oe_secondary_menu a.oe_menu_leaf').click(function() {
            $('.oe_secondary_submenu li').removeClass('active');
        });

        $('.oe_secondary_submenu li a.oe_menu_leaf').click(function() {
            if ($(this).parent().hasClass('active')) {
                window.location.reload();
            } else {
                $('.oe_secondary_submenu li').removeClass('active');
                $(this).parent().addClass('active');
            }
        });

        function GetMenuId() {
            var locationHash = window.location.hash;
            var queryString = locationHash.split('#').join('');
            var urlParams = new URLSearchParams(queryString);
            var menuID = urlParams.get('menu_id');
            return menuID
        }

        function InitMenu() {
            SidemenuEvent();
            var activeMenuItem = $(".f_sub_menu.sidemenu").find("a" + "[data-menu='" + GetMenuId() + "']");
            activeMenuItem.closest(".cssmenu").children("h3").addClass('active');
        }

        function SidemenuEvent() {
            $(".f_sub_menu.sidemenu").mouseleave(MenuClose);
            $(".f_sub_menu.sidemenu > .f_sub_menu_content").mouseover(MenuOpen);
            $(".f_sub_menu.sidemenu").swipe({
                swipeRight:MenuOpen,
                swipeLeft:MenuClose
            });
            function MenuOpen() {
                $(".f_sub_menu.sidemenu").removeClass('mobile_views_menu');
                $('.tableFloatingHeaderOriginal').addClass('tableheaderright');
                if ($('.cssmenu ul:visible').length < 1) {
                    var activeMenuItem = $(".f_sub_menu.sidemenu").find("a" + "[data-menu='" + GetMenuId() + "']");
                    activeMenuItem.parent().addClass('active');
                    activeMenuItem.closest(".cssmenu").children("h3").addClass('active');
                    activeMenuItem.closest(".oe_secondary_submenu").parent().children("a").addClass('active');
                    activeMenuItem.closest(".oe_secondary_menu").before().addClass('active');
                    activeMenuItem.closest(".oe_secondary_menu").css({'display': 'block'});
                    activeMenuItem.closest(".oe_secondary_submenu").css({'display': 'block'});
                }
            }
            function MenuClose() {
               $("li.active").removeClass('active');
               $(".f_sub_menu.sidemenu").addClass('mobile_views_menu');
               $('.oe_secondary_menu').css({'display':'none'});
               $('li .oe_secondary_submenu').css({'display':'none'});
               $('.f_sub_menu_content').find('.oe_menu_toggler').siblings('.oe_secondary_submenu').hide();
               $('.tableFloatingHeaderOriginal').removeClass('tableheaderright');
               $('.cssmenu .oe_menu_toggler').removeClass('active');
            }
        }

        function checkWidth() {
            $(".sidebar_side_menu_toggle").click(function(argument) {
                $('.f_sub_menu').toggle();
            });
            SidemenuEvent();
        }

        $(window).bind('hashchange', function() {
            if ($(".f_sub_menu.sidemenu").find("a" + "[data-menu='" + GetMenuId() + "']").length == 0) {
                $('.cssmenu h3').removeClass('active');
                $("li.active").removeClass('active');
                $('.cssmenu .oe_menu_toggler').removeClass('active');
            }
        });

        setTimeout(function(){
            checkWidth();
        }, 1800);
        $(window).resize(checkWidth);

        InitMenu();
    });
});
