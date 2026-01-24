document.addEventListener("DOMContentLoaded", function () {
    const cyrillicToLatinMap = {
        "а":"a","б":"b","в":"v","г":"g","д":"d","е":"e","ё":"e",
        "ж":"zh","з":"z","и":"i","й":"y","к":"k","л":"l","м":"m",
        "н":"n","о":"o","п":"p","р":"r","с":"s","т":"t","у":"u",
        "ф":"f","х":"h","ц":"ts","ч":"ch","ш":"sh","щ":"sch","ъ":"",
        "ы":"y","ь":"","э":"e","ю":"yu","я":"ya"
    };

    function transliterate(text) {
        return text.toLowerCase().split('').map(char => {
            if (cyrillicToLatinMap[char]) return cyrillicToLatinMap[char];
            else if (/[a-z0-9]/.test(char)) return char;
            else if (char === " " || char === "-" ) return "-";
            else return ""; 
        }).join('').replace(/-+/g, "-").replace(/^-+|-+$/g, "");
    }

    const slugPairs = [
        { source: "name", target: "slug" },
        { source: "title", target: "slug" }
    ];

    slugPairs.forEach(pair => {
        const sourceInput = document.querySelector(`input[name="${pair.source}"]`);
        const targetInput = document.querySelector(`input[name="${pair.target}"]`);

        if (sourceInput && targetInput) {
            sourceInput.addEventListener("input", function () {
                targetInput.value = transliterate(this.value);
            });
        }
    });
});
