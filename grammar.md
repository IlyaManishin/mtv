## Спецификация грамматики в форме Бэкуса — Наура (БНФ)

Формальная грамматика $G[\langle \text{IfStmt} \rangle]$ для распознавания условного оператора в соответствии с ограниченной постановкой задачи определяется следующим образом:

* **Множество нетерминальных символов ($V_N$):** 
  $\{\langle \text{IfStmt} \rangle, \langle \text{Cond} \rangle, \langle \text{Rel} \rangle, \langle \text{Op} \rangle, \langle \text{Assign} \rangle, \langle \text{Ident} \rangle, \langle \text{IdentRest} \rangle, \langle \text{Letter} \rangle, \langle \text{Digit} \rangle\}$
* **Множество терминальных символов ($V_T$):** 
  $\{\text{"if"}, \text{"else"}, \text{"and"}, \text{"or"}, \text{":"}, \text{";"}, \text{"="}, \text{"<"}, \text{">"}, \text{"<="}, \text{">="}, \text{"=="}, \text{"!="}, \text{NEWLINE}, \text{INDENT}, \text{DEDENT}, \text{"a"}..\text{"z"}, \text{"A"}..\text{"Z"}, \text{"\_"}, \text{"0"}..\text{"9"}\}$
* **Начальный символ (аксиома грамматики):** $\langle \text{IfStmt} \rangle$

### 1. Базовая структура правил (с сохранением приоритета операторов)
Этот вариант идеален, если для описания логических условий требуется однозначная грамматика (где `and` имеет более высокий приоритет, чем `or`), либо если в курсовой/лабораторной работе используется классическое разделение уровней:

```bnf
<IfStmt> ::= "if" <Cond> ":" NEWLINE INDENT <Assign> NEWLINE DEDENT "else" ":" NEWLINE INDENT <Assign> NEWLINE DEDENT

<Assign> ::= <Ident> "=" <Ident>

<Cond>   ::= <Cond> "or" <Cond> 
           | <Cond> "and" <Cond> 
           | <Rel>

<Rel>    ::= <Ident> <Op> <Ident>

<Op>     ::= "<" | ">" | "<=" | ">=" | "==" | "!="
```

### 2. Вариант без левой рекурсии (для LL(1) / рекурсивного спуска)
Если ваш парсер пишется методом **рекурсивного спуска**, в документации часто требуют показать грамматику без левой рекурсии и с явным приоритетом операций (`and` связывает сильнее, чем `or`):

```bnf
<IfStmt>   ::= "if" <Cond> ":" NEWLINE INDENT <Assign> NEWLINE DEDENT "else" ":" NEWLINE INDENT <Assign> NEWLINE DEDENT

<Assign>   ::= <Ident> "=" <Ident> ";"

<Cond>     ::= <AndCond> <CondRest>
<CondRest> ::= "or" <AndCond> <CondRest> | ε

<AndCond>  ::= <Rel> <AndRest>
<AndRest>  ::= "and" <Rel> <AndRest> | ε

<Rel>      ::= <Ident> <Op> <Ident>

<Op>       ::= "<" | ">" | "<=" | ">=" | "==" | "!="
```
*(где $\varepsilon$ — пустая цепочка)*

### 3. Лексический уровень (описание идентификатора `<Ident>`)
Если преподаватель требует расписать в БНФ правила вплоть до символов алфавита (а не считать `<Ident>` готовым токеном от лексера), добавьте в конец следующий блок:

```bnf
<Ident>     ::= <Letter> <IdentRest>
<IdentRest> ::= <Letter> <IdentRest> | <Digit> <IdentRest> | ε

<Letter>    ::= "a" | "b" | "c" | ... | "z" | "A" | "B" | "C" | ... | "Z" | "_"
<Digit>     ::= "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"
```