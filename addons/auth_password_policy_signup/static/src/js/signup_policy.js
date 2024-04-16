flectra.define('auth_password_policy_signup.policy',function(require){
"usestrict";

require('web.dom_ready');
varpolicy=require('auth_password_policy');
varPasswordMeter=require('auth_password_policy.Meter');

var$signupForm=$('.oe_signup_form,.oe_reset_password_form');
if(!$signupForm.length){return;}

//hookinpasswordstrengthmeter
//*requirementisthepasswordfield'sminlength
//*recommendationsarefromthemodule
var$password=$('[type=password][minlength]');
varminlength=Number($password.attr('minlength'));
if(isNaN(minlength)){return;}

varmeter=newPasswordMeter(null,newpolicy.Policy({minlength:minlength}),policy.recommendations);
meter.insertAfter($password);
$password.on('input',function(){
    meter.update($password.val());
});
});
