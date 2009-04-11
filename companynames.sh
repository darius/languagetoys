for a in a b c d e f g h i j k l m n o p q r s t u v w x y z; do wget crunchbase.com/companies?c=$a; done
cat companies?c=* | python companynames_extract.py >companynames
