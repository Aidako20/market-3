flectra.define('mail.field_char_emojis',function(require){
"usestrict";

varbasicFields=require('web.basic_fields');
varregistry=require('web.field_registry');
varFieldEmojiCommon=require('mail.field_emojis_common');
varMailEmojisMixin=require('mail.emoji_mixin');

/**
 *ExtensionoftheFieldCharthatwilladdemojissupport
 */
varFieldCharEmojis=basicFields.FieldChar.extend(MailEmojisMixin,FieldEmojiCommon);

registry.add('char_emojis',FieldCharEmojis);

returnFieldCharEmojis;

});
