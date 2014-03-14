// money formatting function
function formatCurrency(value, times, mo) {
    if(value === undefined || value === null) {
        return '';
    }
    if(times !== undefined && times !== null) {
        value *= times;
    }

    var fixed = Number(value).toFixed(2);
    if(value >= 0) {
        fixed = '$' + fixed;
    } else {
        fixed = '-$' + fixed.substring(1);
    }

    if(mo) {
        fixed += ' /mo';
    }
    return fixed;
};

// fast hash function
function hashFNV(str) {
    // implementation of the fnv-1a hashing algorithm
    // http://www.isthe.com/chongo/tech/comp/fnv/#FNV-1a

    var hash = 0x811C9DC5; // magic 32 bit fnv offset 2166136261 in hex
    for (i = 0; i < str.length; i++) {
        char = str.charCodeAt(i); // obtain a byte (ASCII char code 0-255)

        // xor hash with char first as in fnv-1a
        hash ^= char;

        // 2^24 + 2^8 + 2^7 + 2^4 + 2 = 13777618 plus the copy on the left of the +=
        // makes the magic 32 bit fnv prime 16777619 you needed to multiply here
        hash += (hash << 24) + (hash << 8) + (hash << 7) + (hash << 4) + (hash << 1);
    }
    return (hash >>> 0); // remove sign from hash
}

// returns a css-formatted hsla color function deterministically generated from
// an input string
function str2hsla(str, alpha) {
    // obtain last 8 bytes of the hash
    var hash = (hashFNV(str) & 0x00000000ffffffff) >>> 0;

    // obtain hsl values
    var h = hash % 360;
    var s = (hash % 25) + 75; // between 75 and 100
    var l = (hash % 30) + 40; // between 40 and 70

    return "hsla(" + h + ", " + s + "%, " + l + "%, " + alpha + ")";
}

function loads(stringed) {
    res = JSON.parse(stringed);

    function datetime_to_Date(obj) {
        return new Date(obj.year, obj.month-1, obj.day, obj.hour, obj.minute, obj.second, obj.microsecond/1000)
    }

    function deepsearch(obj) {
        for(var i in obj) {
            if(!obj.hasOwnProperty(i)) {
                continue;
            }
            if(obj[i] && obj[i].__type__ == 'datetime') {
                obj[i] = datetime_to_Date(obj[i]);
            } else if(obj[i] && obj[i].__type__ == 'Decimal') {
                obj[i] = Number(obj[i].str);
            } else if(obj[i] && typeof(obj[i]) == 'object') {
                deepsearch(obj[i]);
            }
        }
    }

    deepsearch(res);
    return res;
}

function dumps(obj) {
    function Date_to_datetime(obj) {
        return {
             '__type__': 'datetime',
             'year': obj.getFullYear(),
             'month': obj.getMonth() + 1,
             'day': obj.getDate(),
             'hour': obj.getHours(),
             'minute': obj.getMinutes(),
             'second': obj.getSeconds(),
             'microsecond': obj.getMilliseconds() * 1000
        };
    }

    function deepcopy(obj) {
        var copy = obj.constructor();
        for(var i in obj) {
            console.log("Copying ", i, obj[i])

            if(!obj.hasOwnProperty(i)) {
                console.log("skipping");
                continue;
            }
            if(obj[i] && obj[i].constructor === Date) {
                //console.log("It's a date");
                copy[i] = Date_to_datetime(obj[i]);
            } else if(obj[i] && typeof(obj[i]) == 'object') {
                //console.log("It's an object or array");
                copy[i] = deepcopy(obj[i]);
            } else {
                //console.log("It's a primitive?")
                copy[i] = obj[i];
            }
        }
        return copy;
    }

    copyobj = deepcopy(obj);
    return JSON.stringify(copyobj);
}
