flectra.define('web_flectra.sidemenu', function (require) {
"use strict";

var core = require('web.core');
var session = require('web.session');
var Widget = require('web.Widget');
var config = require('web.config');
var rpc = require('web.rpc');

var SideMenu = Widget.extend({
    init: function() {
        this._super.apply(this, arguments);
        this.is_bound = $.Deferred();
        this._isMainMenuClick = false;
        this.data = {data:{children:[]}};
        this.isLoadflag = true;
        core.bus.on('change_menu_section', this, this.on_change_top_menu);
    },
    start: function() {
        this._super.apply(this, arguments);
        this.$el = $('.f_launcher').find('.oe_application_menu_placeholder');
        return this.bind_menu();
    },
    do_reload: function() {
        var self = this;
        self.bind_menu();
    },
    bind_menu: function() {
        var self = this;
        this.$secondary_menus = this.$el.parents().find('.f_launcher');
        this.$secondary_menus.on('click', 'a[data-menu]', this.on_menu_click);
        this.$el.on('click', 'a[data-menu]', function (event) {
            event.preventDefault();
            var menu_id = $(event.currentTarget).data('menu');
            core.bus.trigger('change_menu_section', menu_id);
        });

        function toggleIcon(e) {
            $(e.target).prev().find('.more-less i').toggleClass('fa-chevron-down fa-chevron-right');
        }

        function toggleCollapse(e) {
            $('.f_launcher .oe_secondary_menu.show').not(e.target).collapse('toggle');
        }

        function closeFullMenu(e) {
            $('.f_launcher_content .app_name, .more-less, .oe_secondary_menu').addClass('hidden');
            $('.f_launcher_content').addClass('mobile_views_menu');
        }

        function  openFullMenu(e) {
            $('.f_launcher_content .app_name, .more-less, .oe_secondary_menu').removeClass('hidden');
            $('.f_launcher_content').removeClass('mobile_views_menu');
        }

        this.$secondary_menus.find('[data-toggle="tooltip"]').tooltip({
            trigger: "hover",
            delay: 500
        });

        this.$secondary_menus.find('#menu_launcher')
            .on('hidden.bs.collapse', toggleIcon)
            .on('shown.bs.collapse', toggleIcon)
            .on('shown.bs.collapse', toggleCollapse);

        // Hide menu on mouseleave and show menu on mouseover
        $('.f_launcher_content')
            .on('mouseleave', closeFullMenu)
            .on('mouseover', openFullMenu);

        // Enable touch gestures for mobile devices
        $(".f_launcher_content").swipe({
            swipeLeft:closeFullMenu,
            swipeRight:openFullMenu,
        });

        // Hide elements on init as default
        if ($('.f_launcher_content').hasClass('mobile_views_menu')) {
            closeFullMenu();
        }

        // Hide second level submenus
        this.$secondary_menus.find('.oe_menu_toggler').siblings('.oe_secondary_submenu').addClass('o_hidden');
        if (self.current_menu) {
            self.open_menu(self.current_menu);
        }
        this.trigger('menu_bound');

        var lazyreflow = _.debounce(this.reflow.bind(this), 200);
        core.bus.on('resize', this, function() {
            if ($(window).width() < 768 ) {
                lazyreflow('all_outside');
                self.is_menus_lite_mode = false;
            } else {
                lazyreflow();
                self.is_menus_lite_mode = 'menus_lite_mode' in window.sessionStorage ? true : false;
                if (self.is_menus_lite_mode) {
                    self.$secondary_menus.addClass('f_launcher_close');
                }
            }
        });
        core.bus.trigger('resize');

        this.is_bound.resolve();
    },

    /**
     * Reflow the menu items and dock overflowing items into a "More" menu item.
     * Automatically called when 'menu_bound' event is triggered and on window resizing.
     *
     * @param {string} behavior If set to 'all_outside', all the items are displayed.
     * If not set, only the overflowing items are hidden.
     */
    reflow: function(behavior) {
        var self = this;
        var $more_container = this.$('#menu_more_container').hide();
        var $more = this.$('#menu_more');
        var $systray = this.$el.parents().find('.oe_systray');

        $more.children('li').insertBefore($more_container);  // Pull all the items out of the more menu

        // 'all_outside' beahavior should display all the items, so hide the more menu and exit
        if (behavior === 'all_outside') {
            // Show list of menu items
            self.$el.show();
            this.$el.find('li').show();
            $more_container.hide();
            return;
        }

        // Hide all menu items
        var $toplevel_items = this.$el.find('li').not($more_container).not($systray.find('li')).hide();
        // Show list of menu items (which is empty for now since all menu items are hidden)
        self.$el.show();
        $toplevel_items.each(function() {
            var remaining_space = self.$el.parent().width() - $more_container.outerWidth();
            self.$el.parent().children(':visible').each(function() {
                remaining_space -= $(this).outerWidth();
            });

            if ($(this).width() >= remaining_space) {
                return false; // the current item will be appended in more_container
            }
            $(this).show(); // show the current item in menu bar
        });
        $more.append($toplevel_items.filter(':hidden').show());
        $more_container.toggle(!!$more.children().length);
        // Hide toplevel item if there is only one
        var $toplevel = self.$el.children("li:visible");
        if ($toplevel.length === 1) {
            $toplevel.hide();
        }
    },
    /**
     * Opens a given menu by id, as if a user had browsed to that menu by hand
     * except does not trigger any event on the way
     *
     * @param {Number} id database id of the terminal menu to select
     */
    open_menu: function (id) {
        var self = this;
        this.current_menu = id;
        session.active_id = id;
        var $clicked_menu, $sub_menu, $main_menu;
        $clicked_menu = this.$el.add(this.$secondary_menus).find('a[data-menu=' + id + ']');
        this.trigger('open_menu', id, $clicked_menu);

        if (this.$secondary_menus.has($clicked_menu).length) {
            $sub_menu = $clicked_menu.parents('.oe_secondary_menu');
            $main_menu = this.$el.find('a[data-menu=' + $sub_menu.data('menu-parent') + ']');
        } else {
            $sub_menu = this.$secondary_menus.find('.oe_secondary_menu[data-menu-parent=' + $clicked_menu.attr('data-menu') + ']');
            $main_menu = $clicked_menu;
        }

        // Activate current main menu
        this.$el.find('.active').removeClass('active');
        $main_menu.parent().addClass('active');

        if(this._isMainMenuClick || this.isLoadflag) {
            var href_id = $sub_menu.attr('id');
            if (href_id && $sub_menu.attr('class').indexOf('in') === -1) {
                window.sessionStorage.removeItem('menus_lite_mode');
                this.is_menus_lite_mode = false;
                if (!this.is_menus_lite_mode) {
                    this.$secondary_menus.find("a[href='#" + href_id + "']").trigger('click');
                }
                this.$secondary_menus.find("a[href='#" + href_id + " i']")
                    .addClass('fa-chevron-up')
                    .removeClass('fa-chevron-down');
            } else {
                if (!this.is_menus_lite_mode) {
                    $clicked_menu.parents('li.panel').find('.oe_main_menu_container .more-less a').trigger('click');
                }
                this.$secondary_menus.find("a[href='#" + href_id + " i']")
                    .addClass('fa-chevron-down')
                    .removeClass('fa-chevron-up');
            }
            this.$el.parents().find('.f_search_launcher').removeClass('launcher_opened');
            this.$el.parents().find('#f_apps_search').find('i').addClass('fa-search').removeClass('fa-times');
        }

        // Hide/Show the leftbar menu depending of the presence of sub-items
        this.$secondary_menus.toggleClass('o_hidden', !$sub_menu.children().length);

        // Activate current menu item and show parents
        this.$secondary_menus.find('.active').removeClass('active');
        if ($main_menu !== $clicked_menu) {
            $clicked_menu.parents().removeClass('o_hidden');
            if ($clicked_menu.is('.oe_menu_toggler')) {
                $clicked_menu.toggleClass('oe_menu_opened').siblings('.oe_secondary_submenu:first').toggleClass('o_hidden');
            } else {
                $clicked_menu.parent().addClass('active');
            }
            this.$secondary_menus.find('.oe_main_menu_container').removeClass('active');
            $clicked_menu.parents('li.panel').find('.oe_main_menu_container').addClass('active');
        }
        // add a tooltip to cropped menu items
        this.$secondary_menus.find('.oe_secondary_submenu li a span').each(function() {
            $(this).tooltip(this.scrollWidth > this.clientWidth ? {title: $(this).text().trim(), placement: 'right'} :'dispose');
        });
        this.isLoadflag = false;
    },
    /**
     * Call open_menu on a menu_item that matches the action_id
     *
     * If `menuID` is a match on this action, open this menu_item.
     * Otherwise open the first menu_item that matches the action_id.
     *
     * @param {Number} id the action_id to match
     * @param {Number} [menuID] a menu ID that may match with provided action
     */
    open_action: function (id, menuID) {
        var $menu = this.$el.add(this.$secondary_menus).find('a[data-action-id="' + id + '"]');
        if (!(menuID && $menu.filter("[data-menu='" + menuID + "']").length)) {
            // menuID doesn't match action, so pick first menu_item
            menuID = $menu.data('menu');
        }
        if (menuID) {
            this.open_menu(menuID);
        }
    },
    /**
     * Process a click on a menu item
     *
     * @param {Number} id the menu_id
     */
    menu_click: function(id) {
        if (!id) { return; }

        // find back the menuitem in dom to get the action
        var $item = this.$el.find('a[data-menu=' + id + ']');
        if (!$item.length) {
            $item = this.$secondary_menus.find('a[data-menu=' + id + ']');
        }
        var action_id = $item.data('action-id');
        // If first level menu doesnt have action trigger first leaf
        if (!action_id) {
            if(this.$el.has($item).length) {
                var $sub_menu = this.$secondary_menus.find('.oe_secondary_menu[data-menu-parent=' + id + ']');
                var $items = $sub_menu.find('a[data-action-id]').filter('[data-action-id!=""]');
                if($items.length) {
                    action_id = $items.data('action-id');
                    id = $items.data('menu');
                }
            }
        }
        if (action_id) {
            this.trigger('menu_click', {
                action_id: action_id,
                id: id,
                previous_menu_id: this.current_menu // Here we don't know if action will fail (in which case we have to revert menu)
            }, $item);
        } else {
            console.log('Menu no action found web test 04 will fail');
        }
        this._isActionId = action_id === undefined ? false : true;
        this.open_menu(id);
    },

    /**
     * Change the current top menu
     *
     * @param {int} [menu_id] the top menu id
     */
    on_change_top_menu: function(menu_id) {
        var self = this;
        this.menu_click(menu_id);
    },
    on_menu_click: function(ev) {
        ev.preventDefault();
        if(!parseInt($(ev.currentTarget).data('menu'))) return;
        this._isMainMenuClick = $(ev.currentTarget).attr('class').indexOf('oe_main_menu') !== -1 ? true : false;
        this.menu_click($(ev.currentTarget).data('menu'));
    },
});

return SideMenu;
});

flectra.define('web_flectra.sidemenu.menu', function(require) {
    "use strict";
    var Menu = require('web.Menu');
    var WebClient = require('web.WebClient');
    var config = require('web.config');
    var data_manager = require('web.data_manager');
    var SideMenu = require('web_flectra.sidemenu');

    WebClient.include({
        show_application: function () {
            this.sidemenu = new SideMenu(this);
            this.sidemenu.appendTo(this.$el.parents().find('.oe_application_menu_placeholder'));
            this.sidemenu.on('menu_click', this, this.on_menu_action);

            if (config.device.size_class < config.device.SIZES.SM) {
                this.sidemenu.is_menus_lite_mode = false;
            } else {
                this.sidemenu.is_menus_lite_mode = 'menus_lite_mode' in window.sessionStorage ? true : false;
            }

            this.bind_hashchange();
            return this._super.apply(this, arguments);
        },

        bind_hashchange: function() {
            var self = this;
            $(window).bind('hashchange', function(e) {
                self.on_hashchange(e);
            });
            var didHashChanged = false;
            $(window).one('hashchange', function () {
                didHashChanged = true;
            });

            var state = $.bbq.getState(true);
            if (_.isEmpty(state) || state.action === "login") {
                self.sidemenu.is_bound.done(function() {
                    self._rpc({
                            model: 'res.users',
                            method: 'read',
                            args: [[session.uid], ['action_id']],
                        })
                        .done(function(result) {
                            if (didHashChanged) {
                                return;
                            }
                            var data = result[0];
                            if(data.action_id) {
                                self.action_manager.doAction(data.action_id[0]);
                                self.sidemenu.open_action(data.action_id[0]);
                            } else {
                                var first_menu_id = self.sidemenu.$el.find("a:first").data("menu");
                                if(first_menu_id) {
                                    self.sidemenu.menu_click(first_menu_id);
                                }
                            }
                        });
                });
            } else {
                $(window).trigger('hashchange');
            }
        },

        on_hashchange: function(event) {
            this._super.apply(this, event);
            if (this._ignore_hashchange) {
                this._ignore_hashchange = false;
                return;
            }
            var self = this;
            this.clear_uncommitted_changes().then(function () {
                var stringstate = $.bbq.getState(false);
                if (!_.isEqual(self._current_state, stringstate)) {
                    var state = $.bbq.getState(true);
                    if(!state.action && state.menu_id) {
                        self.sidemenu.is_bound.done(function() {
                            self.sidemenu.menu_click(state.menu_id);
                        });
                    } else if (state.menu_id) {
                        var action = self.action_manager.getCurrentAction();
                        if (action) {
                            self.sidemenu.open_action(action.id, state.menu_id);
                        }
                    }
                }
                self._current_state = stringstate;
            }, function () {
                if (event) {
                    self._ignore_hashchange = true;
                    window.location = event.originalEvent.oldURL;
                }
            });
        },

        on_menu_action: function(options) {
            var self = this;
            return this.menu_dp.add(data_manager.load_action(options.action_id))
                .then(function (result) {
                    return self.action_mutex.exec(function() {
                        var completed = $.Deferred();
                        $.when(self.action_manager.do_action(result, {
                            clear_breadcrumbs: true,
                            action_menu_id: options.id,
                        })).fail(function() {
                            self.sidemenu.open_menu(options.previous_menu_id);
                        }).always(function() {
                            completed.resolve();
                        });
                        setTimeout(function() {
                            completed.resolve();
                        }, 2000);
                        // We block the menu when clicking on an element until the action has correctly finished
                        // loading. If something crash, there is a 2 seconds timeout before it's unblocked.
                        return completed;
                    });
                });
        },
    });
});

flectra.define('web_flectra.sidemenu.webclient', function(require) {
    "use strict";
    var rpc = require('web.rpc');
    var session = require('web.session');

    var WebClient = require('web.WebClient');

    WebClient.include({
        start : function () {
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
});