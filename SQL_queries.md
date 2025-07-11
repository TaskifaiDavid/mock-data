convert GBP Liberty to Sales:EUR

UPDATE sellout_entries2
SET    sales_eur = ROUND(sales_lc * 1.16, 2)
WHERE  currency = 'GBP'
  AND  reseller = 'Liberty';




Trim off:

UPDATE sellout_entries2
SET    sales_lc = regexp_replace(
           -- replace any en-dash, em-dash, or Unicode minus with ASCII “-”
           regexp_replace(sales_lc, '[\u2013\u2014\u2212]', '-', 'g'),

           -- swap a comma decimal separator for a dot
           ',', '.', 'g'
       )
       -- trim surrounding whitespace
       |> trim()
WHERE  sales_lc !~ '^\s*-?\d+(\.\d+)?\s*$';


