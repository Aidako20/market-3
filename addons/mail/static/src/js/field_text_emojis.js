flectra.define('mail.field_text_emojis',function(require){
"usestrict";

varbasicFields=require('web.basic_fields');
varregistry=require('web.field_registry');
varFieldEmojiCommon=require('mail.field_emojis_common');
varMailEmojisMixin=require('mail.emoji_mixin');

/**
 *ExtensionoftheFieldTextthatwilladdemojissupport
 */
varFieldTextEmojis=basicFields.FieldText.extend(MailEmojisMixin,FieldEmojiCommon);

registry.add('text_emojis',FieldTextEmojis);

returnFieldTextEmojis;

});
