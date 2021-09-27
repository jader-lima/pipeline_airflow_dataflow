import apache_beam as beam
import re
import itertools 
# for datetime manipulation
from datetime import datetime,date
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions
from apache_beam.runners.runner import PipelineState

import argparse

class Etl_olist_template(PipelineOptions):
    @classmethod
    def _add_argparse_args(cls, parser):
        parser.add_value_provider_argument(
            '--input_itens',
            #dest='input_itens', 
            help='Input itens file to process.')
        
        parser.add_value_provider_argument(
            '--input_seller',
            #dest='input_seller', 
            help='Input seller file to process.')
        
        parser.add_value_provider_argument(
            '--input_products',
            #dest='input_products', 
            help='Input products file to process.')
        
        parser.add_value_provider_argument(
            '--input_order',
            #dest='input_order', 
            help='Input order file to process.')
        
        parser.add_value_provider_argument(
            '--input_reviews',
            #dest='input_reviews', 
            help='Input reviews file to process.')
        
        parser.add_value_provider_argument(
            '--input_payments',
            #dest='input_payments', 
            help='Input payments file to process.')
        
        parser.add_value_provider_argument(
            '--input_customer',
            #dest='input_customer', 
            help='Input customer file to process.')
        
        parser.add_value_provider_argument(
            '--output',
            #dest='output',
            help='Output table to write results to.')

        parser.add_value_provider_argument(
            '--partition_date',
            #dest='partition_date',
            help='partition date for big query ingestion.')

    def ListtoStrNovo(self, values, current_date):    
        values = (current_date,values[0],values[7],values[8][0:10],values[9][0:10],values[10][0:10],values[11][0:10],
                  values[12][0:10],values[1],values[2],values[3],values[4],values[13],values[14],values[15],
                  values[16],values[20][0:10],values[27],values[28],values[21],values[22],values[23],values[24],
                  values[25],values[26])
       
        values = ','.join(map(str, values)) 
        #values = re.split(",",re.sub('\r\n', '', re.sub(u'"', '', values)))
        return values

def cleandata(element):
    element = re.sub('\"|\'', '', element)
    thisTuple=element.split(',')
    return thisTuple


def dict_toList(element):   
    item = element[0].split(',')
    for key,value in element[1].items():
        for v in value:
            if(isinstance(v, dict)):
                for key,value in v.items():                
                    item = item + [str(value[0])]
            else:
                item = item + [str(v)]
    return item


 
def retReview(element):  
    if element is not None:
        if len(element) >= 3:
            if len(element[1]) == 32:
                return (element[1],element[2])
            
def retSeller(element):  
    return (element[0],element[2],element[3])     

def retCustomer(element):  
    return (element[0],element[3],element[4])         

def retProd(element):  
    return (element[0],element[1])  
         

                
def reTupless(element):
    l = list(element[1].keys())
    for i in range(len(l)-1):
        item = element[1].get(l[i])
        for x in item:
            for y in element[1].get(l[len(l)-1]):
                if(isinstance(y, list)):
                    yield list(x) + list(y)  
                else:
                    yield list(x) + list(y )
            
            
def ListtoStr(element):    
    str_date = element[8]
    str_date = str_date[0:10]    
    element = str_date,element
    element = ','.join(map(str, element)) 
    return element

def CompleteCleanDate(element):        
    if(element[3] == ''):
        element[3] = '2099-12-31'
        
    if(element[4] == ''):
        element[4] = '2099-12-31'
        
    if(element[5] == ''):
        element[5] = '2099-12-31'
        
    if(element[6] == ''):
        element[6] = '2099-12-31'
        
    if(element[7] == ''):
        element[7] = '2099-12-31'
        
    if(element[17] == ''):
        element[17] = '2099-12-31'
        
    return element


            
def run(argv=None):

    parser = argparse.ArgumentParser()  

    path_args, pipeline_args = parser.parse_known_args()
                
    pipeline_options = PipelineOptions(pipeline_args)

    etl_olist_template = Etl_olist_template()

    p1 = beam.Pipeline(options=pipeline_options)

    global opts

    opts = pipeline_options.view_as(Etl_olist_template)  

    
    output_header='partition_date,order_id,order_status,order_purchase_timestamp,order_approved_at,order_delivered_carrier_date,order_delivered_customer_date,'
    output_header=output_header+'order_estimated_delivery_date,payment_sequential,payment_type,payment_installments,payment_value,review_score,customer_id,customer_city,customer_state,'
    output_header=output_header+'shipping_limit_date,product_id,product_category_name,itens_count,price,freight_value,seller_id,seller_city,seller_state'

    current_date = str(date.today())

    #itens orders

    input_itens_orders = ( 
                          p1 
                          | 'Read itens_orders data' >> beam.io.ReadFromText(opts.input_itens ,skip_header_lines=1)
                          | 'Clean data itens_orders' >> beam.Map(cleandata) 
                       )


    itens_sum_price = (
            input_itens_orders 


                | 'dict for sum prices' >> beam.Map(lambda item: (item[0]+','+item[2]
                                                                                +','+item[3]+','+item[4], float(item[5])) ) 
                | 'Group sum prices' >> beam.CombinePerKey(sum)
    #            | 'Write sum prices' >> beam.io.WriteToText('output/sum_prices.txt')
    )

    itens_count = (
            input_itens_orders 
                | 'dict for count itens' >> beam.Map(lambda item: (item[0]+','+item[2]
                                                                                +','+item[3]+','+item[4], int(item[1])) ) 
                | 'count itens' >> beam.combiners.Count.PerKey()
    #            | 'Write count itens' >> beam.io.WriteToText('output/count_itens.txt')
    )

    join1 = ({'itens_count': itens_count, 'itens_sum_price': itens_sum_price} 
               | 'itens_count + itens_sum_price' >> beam.CoGroupByKey()
    #           | 'mergeddicts 1' >> beam.Map(dict_toList)
    #           | 'dict for join1' >> beam.Map(lambda item: (item[0]+','+item[1]+','+item[3]+','+item[4], int(item[1])) ) 
                                                                                
    #           | 'Write results' >> beam.io.WriteToText('output/result.txt')
    )

    freight_value = (
            input_itens_orders 
                | 'dict for sum freight_value' >> beam.Map(lambda item: (item[0]+','+item[2]
                                                                                +','+item[3]+','+item[4], float(item[6])) ) 
                | 'Group sum freight_value' >> beam.CombinePerKey(sum)
    #            | 'Write count itens' >> beam.io.WriteToText('output/freight_value.txt')
    )

    join2 = ({'join1': join1, 'freight_value': freight_value} 
                | 'join1 + freight_value' >> beam.CoGroupByKey()
                | 'dict to list ' >> beam.Map(dict_toList) 
                | 'create dict join2 ' >> beam.Map(lambda itens: (itens[2], itens))
    #            | 'Write results 2' >> beam.io.WriteToText('output/result_join2.txt')
    )

    sellers = (
            p1
                | 'Read seller data' >> beam.io.ReadFromText(opts.input_seller,skip_header_lines=1)
                | 'Clean data seller' >> beam.Map(cleandata) 
                | 'return seller data except geo id' >> beam.Map(retSeller)
                | 'create dict from seller' >> beam.Map(lambda sellers: (sellers[0], sellers))
    #            | 'Write seller data' >> beam.io.WriteToText('outputs/dept.txt') 
    )

    join3 = ({'join2': join2, 'sellers': sellers} 
                | 'join2 + sellers' >> beam.CoGroupByKey()
    #            | 'dict to list sellers ' >> beam.Map(dict_toList) 
                | 'dict to list sellers' >> beam.FlatMap(reTupless) 
                | 'create dict join3 ' >> beam.Map(lambda itens: (itens[1], itens))#verificar essa linha
    #            | 'Write results 3' >> beam.io.WriteToText('output/_dic_prod_certo.txt')
    )

    #"product_id","product_category_name","product_name_lenght","product_description_lenght",
    #"product_photos_qty","product_weight_g","product_length_cm","product_height_cm","product_width_cm"


    products = (
            p1
                | 'Read prod data' >> beam.io.ReadFromText(opts.input_products,skip_header_lines=1)
                | 'Clean data prod' >> beam.Map(cleandata) 
                | 'return prod data ' >> beam.Map(retProd)
                | 'create dict from prod' >> beam.Map(lambda prod: (prod[0], prod))
    #            | 'Write seller data' >> beam.io.WriteToText('output/prod.txt') 
    )



    join4 = ({'join3': join3, 'products': products} 
                | 'join3 + products' >> beam.CoGroupByKey()
    #            | 'dict to list join4' >> beam.Map(dict_toList) 
                | 'dict to list join4' >> beam.FlatMap(reTupless) 
                | 'dict order id key join 4 ' >> beam.Map(lambda itens: (itens[0], itens))
    #            | 'Write results 4' >> beam.io.WriteToText('output/result_itenssss.txt')
    )

    order = (
            p1
                | 'Read orders data' >> beam.io.ReadFromText(opts.input_order,skip_header_lines=1)
                | 'Clean data orders' >> beam.Map(cleandata) 
    #            | 'return seller data except geo id' >> beam.Map(retSeller)
                | 'create dict from orders' >> beam.Map(lambda order: (order[0], order))
    #            | 'Write seller data' >> beam.io.WriteToText('outputs/dept.txt') 
    )



    reviews = (
            p1
                | 'Read reviews data' >> beam.io.ReadFromText(opts.input_reviews,skip_header_lines=1)
                | 'Clean reviews order' >> beam.Map(cleandata) 
                | 'return order id and review score' >> beam.Map(retReview)
                | 'Check reviews only with id' >> beam.Filter(lambda rev: rev is not None )
                | 'create dict from reviews' >> beam.Map(lambda reviews: (reviews[0], reviews[1]))              
    #            | 'Write reviews data' >> beam.io.WriteToText('outputs/reviews.txt') 
    )

    join5 = ({'order': order, 'reviews': reviews} 
                | 'orders + reviews' >> beam.CoGroupByKey()
                | 'dict to list join5' >> beam.FlatMap(reTupless) 
                | 'create dict join 5 ' >> beam.Map(lambda itens: (itens[0], itens))
    #            | 'Write results join 1' >> beam.io.WriteToText('output/result_order.txt')
    )

    payments = (
            p1
                | 'Read payments data' >> beam.io.ReadFromText(opts.input_payments,skip_header_lines=1)
                | 'Clean payments order' >> beam.Map(cleandata) 
                | 'create dict from payments' >> beam.Map(lambda reviews: (reviews[0], reviews))    
    #            | 'Write payments' >> beam.io.WriteToText('output/payment.txt')
    )

    join6 = ({ 'payments': payments,'join5': join5} 
                | ' payments + join5 ' >> beam.CoGroupByKey()
                | 'dict to list join6' >> beam.FlatMap(reTupless) 
                | 'create dict join 6' >> beam.Map(lambda itens: (itens[6], itens))
    #            | 'Write results join 2' >> beam.io.WriteToText('output/result_payments.txt')
    )

    customer = (
            p1
                | 'Read customer data' >> beam.io.ReadFromText(opts.input_customer,skip_header_lines=1)
                | 'Clean customer order' >> beam.Map(cleandata) 
                | 'return customer id ,state and City' >> beam.Map(retCustomer)
                | 'create dict from customer' >> beam.Map(lambda reviews: (reviews[0], reviews))              
    )

    join7 = ({ 'join6': join6, 'customer': customer} 
                | 'customer + join6' >> beam.CoGroupByKey()
                | 'dict to list join7' >> beam.FlatMap(reTupless) 
                | 'dict order id key join 7  ' >> beam.Map(lambda orders: (orders[0], orders))
    #            | 'Write results join 7' >> beam.io.WriteToText('output/result_orders_esse.txt')
    )


    join8 = ({ 'join7': join7, 'join4': join4} 
                | 'join7 + join4' >> beam.CoGroupByKey()
                | 'dict to list join8' >> beam.FlatMap(reTupless) 
    #            | 'List to string' >> beam.Map(ListtoStr)
                | 'List to string' >> beam.Map(lambda s: etl_olist_template.ListtoStrNovo(s, current_date))
                | 'Date validation' >> beam.Map(CompleteCleanDate)     
                | 'Write results join 8' >> beam.io.WriteToText(opts.output,file_name_suffix='.csv',header=output_header)
    )


    p1.run()

if __name__ == '__main__':
    run()
