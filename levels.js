// Available level packs. Each entry references a level data file,
// loaded on demand when the player selects it from the start menu.
// The level data file should populate window.LEVEL_DATA["<filename>"]
// with an array of arrays of words (one inner array per game level).
// `nextfrac` is the fraction of a level's words the player must guess to
// advance to the next level. 1.0 means "all words"; 0.5 means "half".
window.LEVELS = [
  { name: "Простые Слова", file: "simplewords.js",  nextfrac: 1.0 },
  { name: "Айболит",        file: "aibolit.js",     nextfrac: 0.5 },
  { name: "Кошкин Дом",    file: "koshkindom.js",  nextfrac: 0.5 },
  { name: "Хоббит",         file: "hobbit.js",      nextfrac: 0.5 },
  { name: "Кысь",           file: "kys.js",         nextfrac: 0.5 }
];
