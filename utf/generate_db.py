# Inspired by https://github.com/sethmlarson/utf8.xyz/blob/main/build-db.py
from dataclasses import dataclass
import importlib.resources
import sqlite3
import csv

import platformdirs


db_path = platformdirs.user_cache_path("utf", "treyhunner") / "utf8.db"


@dataclass(slots=True)
class Character:
    ordinal: int
    name: str
    category: str

    @classmethod
    def from_csv_row(cls, row):
        ordinal, name, group = row[:3]
        ordinal = int(ordinal, 16)
        name = name.lower().replace(" ", "-")
        if group == "Sc":
            category = "currency"
        elif "arrow" in name:
            category = "arrows"
        else:
            category = None
        return cls(ordinal, name, category)


def get_character_data():
    # File from https://www.unicode.org/Public/draft/UCD/ucd/UnicodeData.txt
    path = importlib.resources.path("utf", "UnicodeData.txt")
    with open(path) as file:
        return [
            Character.from_csv_row(row)
            for row in csv.reader(file, delimiter=";")
        ]


def make_database():
    db_path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(db_path)
    db.execute(
        """
        CREATE TABLE characters (
            name STRING PRIMARY KEY,
            ordinal INTEGER UNIQUE,
            category STRING DEFAULT '',
            priority INTEGER
        );
        """
    )
    db.execute(
        """
        CREATE TABLE copied_characters (
            name STRING PRIMARY KEY,
            copies INTEGER UNIQUE,
            last_copied DATETIME
        );
        """
    )
    characters = get_character_data()
    populate_chars_table(db, characters)
    db.commit()
    db.close()


def populate_chars_table(db, characters):
    common = common_characters()
    for char in characters:
        if "<" in char.name:  # Skip control characters
            continue
        db.execute(
            """
            INSERT INTO characters (
                name, ordinal, category, priority
            ) VALUES (
                ?, ?, ?, ?
            )
            """,
            (
                char.name,
                char.ordinal,
                char.category,
                common.get(char.ordinal, 0),
            )
        )


def common_characters():
    # Ordinal values for a few thousand commonly used characters
    common_emoji = "😂🤣👍😭🙏😘🥰😍😊🎉😁💕🥺😅🔥🤦🤷🙄😆🤗😉🎂🤔👏🙂😳🥳😎👌💜😔💪✨💖👀😋😏😢👉💗😩💯🌹💞🎈💙😃😡💐😜🙈🤞😄🤤🙌🤪😀💋💀👇💔😌💓🤩🙃😬😱😴🤭😐🌞😒😇🌸😈🎶🎊🥵😞💚🖤💰😚👑🎁💥🙋😑🥴👈💩✅👋🤮😤🤢🌟❗😥🌈💛😝 😫😲🖕🔴🌻🤯💃👊🤬🏃😕⚡☕🍀💦⭐🦋🤨🌺😹🤘🌷💝💤🤝🐰😓💘🍻😟😣🧐😠🤠😻🌙😛🤙🙊🧡🤡🤫🌼🥂😷🤓🥶😶😖🎵🚶😙🍆🤑💅😗🐶🍓✋👅👄🌿🚨📣🤟🍑🍃😮💎📢🌱🙁🍷😪🌚🏆🍒💉❌💢🛒😸🐾👎🚀🎯🍺📌📷🙇💨🍕🏠📸🐇🚩😰👶🌊🐕💫😵🎤🏡🥀🤧🍾🍰🍁🤲👆😯✊💌💸🧁⚽❓🕺😺💧💣🤐🍎🐷🐥💁📍🎀🙅🥇🌝🔫🐱🐣🎧💟👹💍🍼💡😽🍊😨🍫🧢🤕🚫🎼🐻📲👻👿🧚🌮🍭🐟🐸🐝🐈🔵🔪😧🌄😾🤸📱🍇🌴🐢🌃👽🍌📺👐⏰🔔🌅🦄⭕🎥🍋🥚💲📚🐔🎸🥃😿🚗🌎🔊🦅🚿🦆🍉🍬🧸🍨📝🤚📩💵👼💭🌍⚫👧🤜🍿🧿🏀🍏🌳🙉😦⚾🤰🍹🍦🛑🧘🍔🍂🐒🍪🙀🍗🌠🎬🌵🍄🐐🍩🦁🙆📞👸🍅🐍👦💬🥤😼🌾🧀🎮🧠☔🌏🛌🔝🌉🤛🤒👗⚪🌲🍜🐦🍯👮🏅🐼💄👺🔞🎆🎨🍞🎇🦜🐑🐙🦍🔗📖🔹🥓🥒🍸🥧💻🐖📈💊👩🌀💆🥩🎄🌽🤥🐎🆘💏🥕🔮🦀🐠🌛👠🐓🥊🛐🚬🔰🌜🍴🥔🎓👙🗿🥑👯🍍⛽🏁👂🦊👃🦖🐴🎃🦠🌕📦🌌⛳🍧🍟🎹🥞👣🥜🍡🦷🚴🍝🎻🐊🍖🐺🐽🚮🍵🌭🐄🥁🍳👫⌚🔆🐳🌯🦴🥪🦃🎣🔻🐀🐬🍚🤖🐧🦈🏄🏈🧬🌐🔍📴🥦🐯📮🥛🥭🖖🐛🦞🐤🧟🍤🦐🎭🐞🐵🍣🥗🆔🔑👴🤴👵🤳🧨⬛👤🎩🔙🥫🆕🥐👰💳🐚🌆⚓🆗🤱👭🦇👨🦗🦕🏹🐮🚲💑🚒🦎🦉🐂🍈🚭🐘🚙🔨⏩📄🥎🔒🎱🦵🏊🛵🔎👟🆒🔱🦌🥈🚚♈🐜🎲💠🥝🦶👾💮🦑🔺🐁🐌🔷👖💒🐉🎍👕🚽🍥🍐🏫🚂🔐⛄⏳⛅🔜🥣🎋🔶🔸⛔🦸📻👓🥉🐅📊🦝🚪🚘👱🧜🏥⛵🕋📰💇🥬🐨🧹👥⬜📆🥖🐩🤺🛁⌛🔽🍲🦘🥥🛀📅📿🕛🌑🚛🧺📡🐭🗽🆓🎾🏐🎒🆚🌋📉🏒🕐🦙🧙🦟🃏🚢🙍📕👬🐆🔛❕👒🐪🥟🧼🍶🎪👔📎🦚🍠🥨🍮🏩🐃🔅🏰📬➕📛🐏🎺🕌🐋🥋🐲❎🎫📨⛪🦒🎡🧱🎷🚑🚓🚃🏇🌇🙎🚌💶🚜🌰🍛💴👛🧓🥾🐫🥢🧤🚔🎰🧔🥯➖🐹🦂🔘🔄📥📹🛫📏🎠🆙💈🔖🍱🕜🍢🏢🔌🦔🛸🤵👞🔋◾👜🚧♋🏮🐡👘🛹♉🚦🧩🚺🥄🧛🗻♐🦹🏨🏉🦛💼🛴📘🧦🥘🤹♊🚁🔓🏴💿🦓📜👷🚣🧖👳🎎🚹⛺🎅🧂🚐🏏📀🎐🦢🌔🗼🌒🧞🕒🎳🎢🔟⏬🧵🚵🧒♌🧪🚕🧽⛲🏦👚📋♒🌘🐗📠🤼♏🧳🧶📧🏂👢🥅🍙♎🔯🤾♍📯🌓🧻🔁🎽🧣🧗🎴♓📗👪❔🔚📙🧕🏓🧲💹💷◽📃🏧🥙➰🌖🌗🌂🔉🎌📤🀄🔭🚰🧑📒🧧🦏♿🎿🍘🏯🔲🕑🥡💺🔈♑🧴🥮🔧🛬🎑🚤📐📓🎏⏪🏪🧝🚆💂🧥🛶🔕📼🔇🏸💽🦡🌁📔🚄📶🚼🔦🚅🉑🧾🧭🕓🚖🥽📑🕙🤽🔬🚸🎦🗾🔼🕘👡📁🚍🥠🚥🏬🥍🈵🕝🔢🧫🆖🧮🥼➿🤶🕕🏑🔃📵🈶🥏📳🆑📫🕖🚋🔩🕗📂🚇🥌🧰🕚🚏🧯🔏🧷🚷🚎🚉🆎👲🕔💾➗🏺🕎💱🚳🚻📟🉐🈹🥿🕥⏫🔳🕞🔂🚠🏣👝🚊🏭⛎🚈🔀🚾🚝🕍🈴🚟🈯🚯🔤🛂📪🚡🏤🚞🈺📭🕡🛄🕦🚱🕣🈚🈲🔠🛷📇🕤🕧🈸🈳🕢🕠🕟🛃🛅🔡🔣🦰🈁🦱🦲🦳"
    common_characters = "␡¡¢£¤¥¦§¨©ª«¬®¯°±²³´µ¶·¸¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿŁłŃńŅņŇňŊŋŌōŎŏŐőŒœŔŕŖŗŘřŚśŜŝŞşŠšŢţŤťŦŧŨũŪūŬŭŮůŰűŴŵŶŷŸŹźŻżŽžſƆƎƜɐɑɒɔɘəɛɜɞɟɡɢɣɤɥɨɪɬɮɯɰɴɵɶɷɸɹʁʇʌʍʎʞΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩαβγδεζηθικλμνξοπρςστυφχψωАБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдежзийклмнопрстуфхцчшщъыьэюяᴀᴁᴂᴃᴄᴅᴆᴇᴈᴉᴊᴋᴌᴍᴎᴏᴐᴑᴒᴓᴔᴕᴖᴗᴘᴙᴚᴛᴜᴝᴞᴟᴠᴡᴢᴣᴤᴥᴦᴧᴨᴩᴪẞỲỳỴỵỸỹ‐‑‒–—―‖‗‘’‚‛“”„‟†‡•‣․‥…‧‰‱′″‴‵‶‷‸‹›※‼‽‾‿⁀⁁⁂⁃⁄⁅⁆⁇⁈⁉⁊⁋⁌⁍⁎⁏⁐⁑⁒⁓⁔⁕⁗⁰ⁱ⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿ₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎₠₡₢₣₤₥₦₧₨₩₪₫€₭₮₯₰₱₲₳₴₵₶₷₸₹℀℁ℂ℃℄℅℆ℇ℈℉ℊℋℌℍℎℏℐℑℒℓ℔ℕ№℗℘ℙℚℛℜℝ℞℟℠℡™℣ℤ℥Ω℧ℨ℩KÅℬℭ℮ℯℰℱℲℳℴℵℶℷℸ⅁⅂⅃⅄ⅅⅆⅇⅈⅉ⅋ⅎ⅐⅑⅒⅓⅔⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞⅟ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩⅪⅫⅬⅭⅮⅯⅰⅱⅲⅳⅴⅵⅶⅷⅸⅹⅺⅻⅼⅽⅾⅿↄ←↑→↓↔↕↖↗↘↙↚↛↜↝↞↟↠↡↢↣↤↥↦↧↨↩↪↫↬↭↮↯↰↱↲↳↴↵↶↷↸↹↺↻↼↽↾↿⇀⇁⇂⇃⇄⇅⇆⇇⇈⇉⇊⇋⇌⇍⇎⇏⇐⇑⇒⇓⇔⇕⇖⇗⇘⇙⇚⇛⇜⇝⇞⇟⇠⇡⇢⇣⇤⇥⇦⇧⇨⇩⇪⇫⇬⇭⇮⇯⇰⇱⇲⇳⇴⇵⇶⇷⇸⇹⇺⇻⇼⇽⇾⇿∀∁∂∃∄∅∆∇∈∉∊∋∌∍∎∏∐∑−∓∔∕∖∗∘∙√∛∜∝∞∟∠∡∢∣∤∥∦∧∨∩∪∫∬∭∮∯∰∱∲∳∴∵∶∷∸∹∺∻∼∽∾∿≀≁≂≃≄≅≆≇≈≉≊≋≌≍≎≏≐≑≒≓≔≕≖≗≘≙≚≛≜≝≞≟≠≡≢≣≤≥≦≧≨≩≪≫≬≭≮≯≰≱≲≳≴≵≶≷≸≹≺≻≼≽≾≿⊀⊁⊂⊃⊄⊅⊆⊇⊈⊉⊊⊋⊌⊍⊎⊏⊐⊑⊒⊓⊔⊕⊖⊗⊘⊙⊚⊛⊜⊝⊞⊟⊠⊡⊢⊣⊤⊥⊦⊧⊨⊩⊪⊫⊬⊭⊮⊯⊰⊱⊲⊳⊴⊵⊶⊷⊸⊹⊺⊻⊼⊽⊾⊿⋀⋁⋂⋃⋄⋅⋆⋇⋈⋉⋊⋋⋌⋍⋎⋏⋐⋑⋒⋓⋔⋕⋖⋗⋘⋙⋚⋛⋜⋝⋞⋟⋠⋡⋢⋣⋤⋥⋦⋧⋨⋩⋪⋫⋬⋭⋮⋯⋰⋱⌀⌁⌂⌃⌄⌅⌆⌇⌈⌉⌊⌋⌐⌑⌒⌓⌔⌕⌖⌗⌘⌙⌠⌡⌢⌣⌤⌥⌦⌧⌨⌫⌬⎛⎜⎝⎞⎟⎠⎡⎢⎣⎤⎥⎦⎧⎨⎩⎪⎫⎬⎭⏎⏏⏚⏛⏱⏲␢␣─━│┃┄┅┆┇┈┉┊┋┌┍┎┏┐┑┒┓└┕┖┗┘┙┚┛├┝┞┟┠┡┢┣┤┥┦┧┨┩┪┫┬┭┮┯┰┱┲┳┴┵┶┷┸┹┺┻┼┽┾┿╀╁╂╃╄╅╆╇╈╉╊╋╌╍╎╏═║╒╓╔╕╖╗╘╙╚╛╜╝╞╟╠╡╢╣╤╥╦╧╨╩╪╫╬╭╮╯╰╱╲╳╴╵╶╷╸╹╺╻╼╽╾╿▀▁▂▃▄▅▆▇█▉▊▋▌▍▎▏▐░▒▓▔▕▖▗▘▙▚▛▜▝▞▟■□▢▣▤▥▦▧▨▩▪▫▬▭▮▯▰▱▲△▴▵▶▷▸▹►▻▼▽▾▿◀◁◂◃◄◅◆◇◈◉◊○◌◍◎●◐◑◒◓◔◕◖◗◘◙◚◛◜◝◞◟◠◡◢◣◤◥◦◧◨◩◪◫◬◭◮◯◰◱◲◳◴◵◶◷◸◹◺◻◼◿☀☁☂☃☄★☆☇☈☉☊☋☌☍☎☏☐☑☒☓☖☗☘☙☚☛☜☝☞☟☠☡☢☣☤☥☦☧☨☩☪☫☬☭☮☯☰☱☲☳☴☵☶☷☸☹☺☻☼☽☾☿♀♁♂♃♄♅♆♇♔♕♖♗♘♙♚♛♜♝♞♟♠♡♢♣♤♥♦♧♨♩♪♫♬♭♮♯♲♳♴♵♶♷♸♹♺♻♼♽♾⚀⚁⚂⚃⚄⚅⚐⚑⚒⚔⚕⚖⚗⚘⚙⚚⚛⚜⚝⚞⚟⚠⚢⚣⚤⚥⚦⚧⚨⚩⚬⚭⚮⚯⚰⚱⚲⚳⚴⚵⚶⚷⚸⚹⚺⚻⚼⛀⛁⛂⛃⛢⛤⛥⛦⛧⛨⛩⛫⛬⛭⛮⛯⛰⛱⛴⛶⛷⛸⛹⛻⛼⛾⛿✁✂✃✄✆✇✈✉✌✍✎✏✐✑✒✓✔✕✖✗✘✙✚✛✜✝✞✟✠✡✢✣✤✥✦✧✩✪✫✬✭✮✯✰✱✲✳✴✵✶✷✸✹✺✻✼✽✾✿❀❁❂❃❄❅❆❇❈❉❊❋❍❏❐❑❒❖❘❙❚❛❜❝❞❟❠❡❢❣❤❥❦❧➔➘➙➚➛➜➝➞➟➠➡➢➣➤➥➦➧➨➩➪➫➬➭➮➯➱➲➳➴➵➶➷➸➹➺➻➼➽➾⟰⟱⟲⟳⟴⟵⟶⟷⟸⟹⟺⟻⟼⟽⟾⟿⤀⤁⤂⤃⤄⤅⤆⤇⤈⤉⤊⤋⤌⤍⤎⤏⤐⤑⤒⤓⤔⤕⤖⤗⤘⤙⤚⤛⤜⤝⤞⤟⤠⤡⤢⤣⤤⤥⤦⤧⤨⤩⤪⤫⤬⤭⤮⤯⤰⤱⤲⤳⤴⤵⤶⤷⤸⤹⤺⤻⤼⤽⤾⤿⥀⥁⥂⥃⥄⥅⥆⥇⥈⥉⥊⥋⥌⥍⥎⥏⥐⥑⬀⬁⬂⬃⬄⬅⬆⬇⬈⬉⬊⬋⬌⬍⬎⬏⬐⬑⬒⬓⬔⬕⬖⬗⬘⬙⬚ⱠⱡⱣⱥⱦⱭⱯⱰ⸢⸣⸤⸥⸮〃〄ﬀﬁﬂﬃﬄﬅﬆ﴾﴿﷼︐︑︒︓︔︕︖︗︘︙︰︱︲︳︴︵︶︷︸︹︺︻︼︽︾︿﹀﹁﹂﹃﹄﹅﹆﹉﹊﹋﹌﹍﹎﹏﹐﹑﹒﹔﹕﹖﹗﹘﹙﹚﹛﹜﹝﹞﹟﹠﹡﹢﹣﹤﹥﹦﹨ ﹩﹪﹫\ufeff！＂＃＄％＆＇（）＊＋，－．／０１２３４５６７８９：；＜＝＞？＠ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ［＼］＾＿｀ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ｛｜｝～｟｠￠￡￢￣￤￥￦￼�"
    emoji_ordinals = [ord(c) for c in common_emoji]
    character_ordinals = [ord(c) for c in common_characters]
    return (
        dict.fromkeys(emoji_ordinals, 10)
        | dict.fromkeys(character_ordinals, 8)
    )
