# FoodDiary

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Этот инструмент я использую для приблизительного расчета количества калорий, которые я получил за день, а также контроля за балансом БЖУ.

Знаю, есть целый выводок приложений для решения этой задачи, но мне не нравится ни одно из них: какое-то теряет данные, где-то неудобный интерфейс, и почти все назойливо пытаются всучить платную подписку. А мне нужна одна-единственная простая функция!

## Как использовать? 

1. В течении дня я записываю всё, что съел, в журнал (`journal.yaml`). Если съел что-то новое — добавляю это в справочник (`catalog.yaml`).
2. Когда хочу определить, не перевалил ли за норму калорий в сутки и соблюдается ли баланс БЖУ — запускаю скрипт вывода статистики (`scripts/statistics.py`). 
3. Каждое утро запускаю скрипт создания нового журнала (`scripts/new_journal.py`) — он создает копию журнала в папке `history`, а потом очищает его.

Скрипт вывода статистики отображает:

1. Общую калорийность в разрезе съеденных продуктов;
2. Количество белков, жиров и углеводов для каждого съеденного продукта;
3. Процентное соотношение всех потребленных в течении дня белков, жиров и углеводов.

Пример:

```
ПРОДУКТ                                       К          Б          Ж          У         

Вареная ветчина "Семейная"                    306        24         21         5         
Сосиски "Восточные"                           121        10         9          0         
Яблоко                                        56         1          1          14        

ИТОГО                                         483        35         31         19        

БАЛАНС БЖУ СЕГОДНЯ                                       41%        36%        22%       
ЦЕЛЕВОЙ БАЛАНС БЖУ                                       30%        20%        50%       
```

Скрипт создания нового журнала обычно не выводит ничего.