module.exports = {
    root: true,
    env: { node: true, browser: true },
    extends: ['plugin:vue/vue3-recommended', 'eslint:recommended', 'plugin:@typescript-eslint/recommended', 'prettier'],
    parser: 'vue-eslint-parser',
    parserOptions: { parser: '@typescript-eslint/parser', ecmaVersion: 2020, sourceType: 'module' },
    rules: {}
}
