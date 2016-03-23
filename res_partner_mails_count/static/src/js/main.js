openerp.res_partner_mails_count = function(instance){
	instance.mail.Wall.include({
		init: function(){
			this._super.apply(this, arguments);
			delete this.defaults.model;
		}
	});
};
