# Спецификация грамматики в форме Бэкуса — Наура (БНФ)

Формальная грамматика $G = \langle V_N, V_T, P, S \rangle$ для распознавания условного оператора языка Python (`if-else`) определяется следующим кортежем:

* **Множество нетерминальных символов ($V_N$):**  
  `{ <if_stmt>, <condition>, <logical_term>, <primary_cond>, <comparison>, <Op>, <assignment>, <ident> }`

* **Множество терминальных символов ($V_T$):**  
  `{ "if", "else", "and", "or", ":", "=", "(", ")", "<", ">", "<=", ">=", "==", "!=", NEWLINE, INDENT, DEDENT, <ident> }`

* **Целевой символ (аксиома грамматики $S$):**  
  `<if_stmt>`

---

## 1. Каноническая грамматика БНФ (с приоритетом операций)

Данная грамматика описывает синтаксис языка с явной иерархией приоритетов: оператор `and` связывает сильнее, чем `or`, поддерживаются группирующие скобки `(...)`, операторы сравнения `<Op>` и простые логические переменные.

```bnf
<if_stmt>       ::= "if" <condition> ":" NEWLINE INDENT <assignment> NEWLINE DEDENT "else" ":" NEWLINE INDENT <assignment> NEWLINE DEDENT

<condition>     ::= <condition> "or" <logical_term>
                  | <logical_term>

<logical_term>  ::= <logical_term> "and" <primary_cond>
                  | <primary_cond>

<primary_cond>  ::= "(" <condition> ")"
                  | <comparison>
                  | <ident>

<comparison>    ::= <ident> <Op> <ident>

<Op>            ::= "<" | ">" | "<=" | ">=" | "==" | "!="

<assignment>    ::= <ident> "=" <ident>
```

---

## 2. Грамматика без левой рекурсии (для метода рекурсивного спуска / LL(1))

Для реализации синтаксического анализатора методом рекурсивного спуска леворекурсивные правила преобразуются в праворекурсивные с использованием пустой цепочки $\varepsilon$:

```bnf
<if_stmt>          ::= "if" <condition> ":" NEWLINE INDENT <assignment> NEWLINE DEDENT "else" ":" NEWLINE INDENT <assignment> NEWLINE DEDENT

<condition>        ::= <logical_term> <condition_tail>
<condition_tail>   ::= "or" <logical_term> <condition_tail>
                     | ε

<logical_term>     ::= <primary_cond> <term_tail>
<term_tail>        ::= "and" <primary_cond> <term_tail>
                     | ε

<primary_cond>     ::= "(" <condition> ")"
                     | <ident> <comparison_tail>

<comparison_tail>  ::= <Op> <ident>
                     | ε

<Op>               ::= "<" | ">" | "<=" | ">=" | "==" | "!="

<assignment>       ::= <ident> "=" <ident>
```

*(где $\varepsilon$ — пустая цепочка)*

---

## 3. Лексический уровень (структура идентификатора `<ident>`)

Правила формирования идентификаторов на лексическом уровне:

```bnf
<ident>         ::= ( <letter> | "_" ) { <letter> | <digit> | "_" }
<letter>        ::= "a" | ... | "z" | "A" | ... | "Z"
<digit>         ::= "0" | ... | "9"
```