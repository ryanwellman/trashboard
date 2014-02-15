// money formatting function
function formatCurrency(value) {
    return Number(value).toFixed(2);
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