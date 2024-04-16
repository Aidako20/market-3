flectra.define('mail.emojis',function(require){
"usestrict";

/**
 *Thismoduleexportsthelistofallavailableemojisontheclientside.
 *Anemojiobjecthasthefollowingproperties:
 *
 *     -{string[]}sources:thecharacterrepresentationsoftheemoji
 *     -{string}unicode:theunicoderepresentationoftheemoji
 *     -{string}description:thedescriptionoftheemoji
 */

/**
 *Thisdatarepresentalltheavailableemojisthataresupportedontheweb
 *client:
 *
 *-key:thisisthesourcerepresentationofanemoji,i.e.its"character"
 *       representation.Thisisastringthatcanbeeasilytypedbythe
 *       userandthentranslatedtoitsunicoderepresentation(seevalue)
 *-value:thisistheunicoderepresentationofanemoji,i.e.its"true"
 *         representationinthesystem.
 */
vardata={
    ":)":            "😊",
    ":-)":           "😊",//alternative(alt.)
    "=)":            "😊",//alt.
    ":]":            "😊",//alt.
    ":D":            "😃",
    ":-D":           "😃",//alt.
    "=D":            "😃",//alt.
    "xD":            "😆",
    "XD":            "😆",//alt.
    "x'D":           "😂",
    ";)":            "😉",
    ";-)":           "😉",//alt.
    "B)":            "😎",
    "8)":            "😎",//alt.
    "B-)":           "😎",//alt.
    "8-)":           "😎",//alt.
    ";p":            "😜",
    ";P":            "😜",//alt.
    ":p":            "😋",
    ":P":            "😋",//alt.
    ":-p":           "😋",//alt.
    ":-P":           "😋",//alt.
    "=P":            "😋",//alt.
    "xp":            "😝",
    "xP":            "😝",//alt.
    "o_o":           "😳",
    ":|":            "😐",
    ":-|":           "😐",//alt.
    ":/":            "😕",//alt.
    ":-/":           "😕",//alt.
    ":(":            "😞",
    ":@":            "😱",
    ":O":            "😲",
    ":-O":           "😲",//alt.
    ":o":            "😲",//alt.
    ":-o":           "😲",//alt.
    ":'o":           "😨",
    "3:(":           "😠",
    ">:(":           "😠",//alt.
    "3:)":           "😈",
    ">:)":           "😈",//alt.
    ":*":            "😘",
    ":-*":           "😘",//alt.
    "o:)":           "😇",
    ":'(":           "😢",
    ":'-(":          "😭",
    ":\"(":          "😭",//alt.
    "<3":            "❤️",
    "&lt;3":         "❤️",
    ":heart":        "❤️",//alt.
    "</3":           "💔",
    "&lt;/3":        "💔",
    ":heart_eyes":   "😍",
    ":turban":       "👳",
    ":+1":           "👍",
    ":-1":           "👎",
    ":ok":           "👌",
    ":poop":         "💩",
    ":no_see":       "🙈",
    ":no_hear":      "🙉",
    ":no_speak":     "🙊",
    ":bug":          "🐞",
    ":kitten":       "😺",
    ":bear":         "🐻",
    ":snail":        "🐌",
    ":boar":         "🐗",
    ":clover":       "🍀",
    ":sunflower":    "🌹",
    ":fire":         "🔥",
    ":sun":          "☀️",
    ":partly_sunny:":"⛅️",
    ":rainbow":      "🌈",
    ":cloud":        "☁️",
    ":zap":          "⚡️",
    ":star":         "⭐️",
    ":cookie":       "🍪",
    ":pizza":        "🍕",
    ":hamburger":    "🍔",
    ":fries":        "🍟",
    ":cake":         "🎂",
    ":cake_part":    "🍰",
    ":coffee":       "☕️",
    ":banana":       "🍌",
    ":sushi":        "🍣",
    ":rice_ball":    "🍙",
    ":beer":         "🍺",
    ":wine":         "🍷",
    ":cocktail":     "🍸",
    ":tropical":     "🍹",
    ":beers":        "🍻",
    ":ghost":        "👻",
    ":skull":        "💀",
    ":et":           "👽",
    ":alien":        "👽",//alt.
    ":party":        "🎉",
    ":trophy":       "🏆",
    ":key":          "🔑",
    ":pin":          "📌",
    ":postal_horn":  "📯",
    ":music":        "🎵",
    ":trumpet":      "🎺",
    ":guitar":       "🎸",
    ":run":          "🏃",
    ":bike":         "🚲",
    ":soccer":       "⚽️",
    ":football":     "🏈",
    ":8ball":        "🎱",
    ":clapper":      "🎬",
    ":microphone":   "🎤",
    ":cheese":       "🧀",
};

//listofemojisinadictionary,indexedbyemojiunicode
varemojiDict={};
_.each(data,function(unicode,source){
    if(!emojiDict[unicode]){
        emojiDict[unicode]={
            sources:[source],
            unicode:unicode,
            description:source,
        };
    }else{
        emojiDict[unicode].sources.push(source);
    }
});

varemojis=_.values(emojiDict);

returnemojis;

});
