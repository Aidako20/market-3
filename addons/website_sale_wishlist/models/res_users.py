fromflectraimportapi,fields,models
fromflectra.httpimportrequest


classResUsers(models.Model):
    _inherit="res.users"

    def_check_credentials(self,password,env):
        """Makeallwishlistsfromsessionbelongtoitsowneruser."""
        result=super(ResUsers,self)._check_credentials(password,env)
        ifrequestandrequest.session.get('wishlist_ids'):
            self.env["product.wishlist"]._check_wishlist_from_session()
        returnresult
