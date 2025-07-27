import sqlalchemy
from sqlalchemy import func
from models import Customer, Item, Purchase, PurchaseDetail, app,db
from flask import Response, render_template, request
from datetime import datetime

#ページ遷移

# トップページ
@app.route('/')
def index():
    customers = Customer.query.all()
    return render_template('1_index.html', customers = customers)

# 商品ページ
@app.route('/item')
def item():
    items = Item.query.all()
    return render_template('2_item.html', items = items)

# 購入ページ
@app.route('/purchase')
def purchase():
    customers = Customer.query.all()
    items = Item.query.all()
    return render_template('3_purchase.html', customers = customers, items = items)

# 購入情報検索/分析ページ
@app.route('/purchase_data_statistics')
def purchase_data_statistics():
    joined_purchase_details = db.session.query(Purchase, PurchaseDetail,Customer,Item).join(PurchaseDetail, Purchase.purchase_id == PurchaseDetail.purchase_id).join(Customer, Purchase.customer_id == Customer.customer_id).join(Item, PurchaseDetail.item_id == Item.item_id).all()
    print(joined_purchase_details)
    customers = Customer.query.all()
    items = Item.query.all()
    return render_template('4_purchase_data_statistics.html', joined_purchase_details = joined_purchase_details, customers = customers, items = items)

# 機能系
# 1-1 顧客新規登録
@app.route('/add_customer', methods=['POST'])
def add_customer():
    customer_id = request.form['input-customer-id']
    customer_name = request.form['input-customer-name']
    customer_age = request.form['input-customer-age']
    customer_gender = request.form['input-gender']
    customer = Customer(customer_id, customer_name, customer_age, customer_gender)
    try:    
        db.session.add(customer)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        return render_template('error.html', error = '顧客IDが重複しています')

    return render_template('1-1_confirm_added_customer.html', customer = customer)

# 1-2 性別で顧客一覧から抽出
@app.route('/select_gender', methods=['POST'])
def select_gender():
    gender = request.form['input-gender2']
    customers = Customer.query.filter_by(gender=gender).all()
    return render_template('1-2_result_select_gender.html', customers = customers)

# 2-1 商品新規登録
@app.route('/add_item', methods=['POST'])
def add_item():
    item_id = request.form['input-item-id']
    item_name = request.form['input-item-name']
    item_price = request.form['input-item-price']   
    item = Item(item_id, item_name, item_price)
    try:
        db.session.add(item)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        return render_template('error.html', error = '商品IDが重複しています')

    return render_template('2-1_confirm_added_item.html', item = item)

# 3 商品削除
@app.route('/delete_item', methods=['POST'])
def delete_item():
    item_id = request.form['input-item-id']
    item = Item.query.filter_by(item_id=item_id).first()
    try:
        if item:
            db.session.delete(item)
            db.session.commit() 
        return render_template('2-2_confirm_deleted_item.html', item = item)
    except sqlalchemy.exc.IntegrityError:
        return render_template('error.html', error = '商品IDが見つかりません')

# 4 商品更新
@app.route('/update_item', methods=['POST'])
def update_item():
    item_id = request.form['input-item-id']
    item_name = request.form['input-item-name']
    item_price = request.form['input-item-price']
    item = Item.query.filter_by(item_id=item_id).first()
    try:
        if item:
            item.item_name = item_name
            item.price = item_price
            db.session.add(item)
            db.session.commit() 
        return render_template('2-3_confirm_updated_item.html', item = item)
    except sqlalchemy.exc.IntegrityError:
        return render_template('error.html', error = '商品IDが見つかりません')

# 5 商品名で抽出
@app.route('/search_item', methods=['POST'])
def search_item():
    result_type = '商品名で抽出'

    item_name = request.form['input-item-name']
    items = Item.query.filter(Item.item_name.like(f'%{item_name}%')).all()
    return render_template('2-4_result_search_item.html', items = items, result_type = result_type)

# 6 単価で並び替え
@app.route('/sort_item', methods=['POST'])
def sort_item():
    result_type = '単価で並び替え'
    order_type = request.form['order-type']
    if order_type == 'ascending':
        items = Item.query.order_by(Item.price).all()
    else:
        items = Item.query.order_by(Item.price.desc()).all()
    return render_template('2-4_result_search_item.html', items = items, result_type = result_type)

# 7 CSVダウンロード
@app.route('/download_csv', methods=['POST'])
def download_csv():
    items = Item.query.all()
    csv_data = [item.to_csv_row() for item in items]
    csv_data = '\n'.join(csv_data)
    
    # BOM付きUTF-8でエンコード
    csv_bytes = '\ufeff' + csv_data  # BOMを先頭に追加
    csv_bytes = csv_bytes.encode('utf-8')
    
    return Response(
        csv_bytes, 
        mimetype='text/csv; charset=utf-8',
        headers={'Content-Disposition': 'attachment; filename=items.csv'}
    )

# 3-1 購入情報登録
@app.route('/add_purchase', methods=['POST'])
def add_purchase():
    customer_name = request.form['input-customer-name']
    item_name1 = request.form['input-item-name1']
    item_name2 = request.form['input-item-name2']
    purchase_date = request.form['input-purchase-date']
    print("item_name1:", item_name1)
    print("item_name2:", item_name2)
    customer = Customer.query.filter_by(customer_name=customer_name).first()
    
    purchase_date = datetime.strptime(purchase_date, '%Y-%m-%d')
    purchase = Purchase(customer.customer_id, purchase_date)
    try:
        db.session.add(purchase)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        return render_template('error.html', error = '購入情報が重複しています')

    quantity1 = request.form['input-quantity1']
    item1 = Item.query.filter_by(item_name=item_name1).first()
    purchase_item1 = PurchaseDetail(purchase.purchase_id, item1.item_id, quantity1)
    print("item1:", item1)
    try:
        db.session.add(purchase_item1)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        return render_template('error.html', error = '購入情報が重複しています')
    item2 = Item.query.filter_by(item_name=item_name2).first()

    if item2:
        quantity2 = request.form['input-quantity2']
        purchase_item2 = PurchaseDetail(purchase.purchase_id, item2.item_id, quantity2)
        try:
            db.session.add(purchase_item2)
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            return render_template('error.html', error = '購入情報が重複しています')

    return render_template('3-1_confirm_added_purchase.html', purchase = purchase)

# 3-2 購入情報削除
@app.route('/delete_purchase', methods=['POST'])
def delete_purchase():
    purchase_id = request.form['input-purchase-id']
    purchase = Purchase.query.filter_by(purchase_id=purchase_id).first()
    try:
        if purchase:
            db.session.delete(purchase)
            db.session.commit()
        return render_template('3-2_confirm_deleted_purchase.html', purchase = purchase)
    except sqlalchemy.exc.IntegrityError:
        return render_template('error.html', error = '購入情報が見つかりません')

# 4-1 購入情報検索
@app.route('/search_purchase', methods=['POST'])
def search_purchase():
    item_name = request.form['input-item-name']
    customer_name = request.form['input-customer-name']
    purchase_date = request.form['input-purchase-date']
    if item_name:
        search_target = "%{}%".format(item_name)
        items = Item.query.filter(Item.item_name.like(search_target)).all()
        item_id_list = []
        for item in items:
            item_id_list.append(item.item_id)
    if customer_name:
        customer = Customer.query.filter_by(customer_name=customer_name).first()
        customer_id = customer.customer_id
    else:
        customer = None
    if  purchase_date:
        purchase_date = datetime.strptime(purchase_date, '%Y-%m-%d')
    # else:
    #     purchase_date = None

    is_customer_or_date = True
    if customer and purchase_date:
        purchases = Purchase.query.filter(Purchase.customer_id == customer_id,Purchase.purchase_date == purchase_date).all()

    elif customer:
        purchases = Purchase.query.filter(Purchase.customer_id == customer_id).all()

    elif purchase_date:
        purchases = Purchase.query.filter(Purchase.purchase_date == purchase_date).all()
    else:
        is_customer_or_date = False
    
    if is_customer_or_date:
        # purchase_id_list = []
        # for purchase in purchases:
        #     purchase_id_list.append(purchase.purchase_id)
        purchase_id_list = [purchase.purchase_id for purchase in purchases]

    if is_customer_or_date and item_name:
        purchase_details = PurchaseDetail.query.filter(PurchaseDetail.item_id.in_(purchase_id_list),PurchaseDetail.item_id.in_(item_id_list),PurchaseDetail.purchase_id.in_(purchase_id_list)).all()
        return render_template('4-1_result_search_purchase.html', purchase_details = purchase_details)
    elif is_customer_or_date:
        purchase_details = PurchaseDetail.query.filter(PurchaseDetail.purchase_id.in_(purchase_id_list)).all()
        return render_template('4-1_result_search_purchase.html', purchase_details = purchase_details)
    elif item_name:
        purchase_details = PurchaseDetail.query.filter(PurchaseDetail.item_id.in_(item_id_list)).all()
        return render_template('4-1_result_search_purchase.html', purchase_details = purchase_details)
    else:
        return render_template('error.html', error = '購入情報が見つかりません')
    
# 4-2 総顧客数算出
@app.route('/count_customers', methods=['POST'])
def count_customers():
    statistics_type = '総顧客数'
    number_of_customers = db.session.query(Customer).count()
    result = str(number_of_customers)+"人"
    return render_template('4-2_result_statistics.html', result = result, statistics_type = statistics_type)

# 4-2 総販売数量算出
@app.route('/count_quantity', methods=['POST'])
def count_quantity():
    statistics_type = '総販売数量'
    total_quantity = db.session.query(func.sum(PurchaseDetail.quantity)).first()
    for row in total_quantity:
        result = row
    result = str(result)+"個"
    return render_template('4-2_result_statistics.html', result = result, statistics_type = statistics_type)

# 4-3 総売上金額算出
@app.route('/total_sales', methods=['POST'])
def total_sales():
    statistics_type = '総売上金額'
    joined_table  = db.session.query(PurchaseDetail.purchase_id,Item.item_id,Item.price,PurchaseDetail.quantity).join(PurchaseDetail, PurchaseDetail.item_id == Item.item_id).all()
    total_sales = 0
    for purchase_id, item_id, price, quantity in joined_table:
        total_sales += price * quantity

    # 小数点以下を切り捨て
    total_sales = int(total_sales)
    result = str(total_sales)+"円"
    return render_template('4-2_result_statistics.html', result = result, statistics_type = statistics_type)

# 4-4 販売数量商品別ランキング
@app.route('/sales_ranking', methods=['POST'])
def sales_ranking():
    statistics_type = '販売数量商品別ランキング'
    joined_table = db.session.query(Item.item_id,Item.item_name,func.sum(PurchaseDetail.quantity)).join(PurchaseDetail, PurchaseDetail.item_id == Item.item_id).group_by(Item.item_id).order_by(func.sum(PurchaseDetail.quantity).desc()).all()
    result = []
    for item_id, item_name, quantity in joined_table:
        result.append(f"{item_name}：{quantity}個")
    return render_template('4-4_result_sales_ranking.html', result = result, statistics_type = statistics_type)

if __name__ == '__main__':
    app.run(debug=True)
