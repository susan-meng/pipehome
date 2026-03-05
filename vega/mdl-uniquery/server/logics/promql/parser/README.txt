1. 扩展 promql 语句中指标标识符中含有点号 "." 的情况，例如指标名称为 a.b.c。文件位置 lex.go 的 lexKeywordOrIdentifier 方法。
2. 扩展 promql 语句中 labels 标识符支持标识符中包含 ':' 和 '.'。例如 o:n!~"bar"。文件位置 lex.go 的 lexIdentifier 方法
3. 扩展 promql 语句中 on 指定的 label 字段的是否是labels的判断。lex.go 中的 isLabel 方法里的 isAlphaNumeric 方法换成 isAlphaNumericDot 方法。
4. 扩展 promql 语句中的 range 支持 auto，使得 range 能根据 step 自适应调整。
5. 词法文件生成：在 server/logics/promql/parser 目录下执行 goyacc -l -v "" -o generated_parser.y.go generated_parser.y