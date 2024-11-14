from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)  


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    sold = db.Column(db.Integer, default=0)  


# 商品リストの表示
@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

# 商品追加
@app.route('/add', methods=['POST'])
def add_product():
    name = request.form['name']
    stock = int(request.form['stock'])
    price = float(request.form['price'])

    new_product = Product(name=name, stock=stock, price=price)
    db.session.add(new_product)
    db.session.commit()
    return redirect(url_for('index'))

# 商品販売
@app.route('/sell/<int:id>', methods=['POST'])
def sell_product(id):
    product = Product.query.get(id)
    if product.sold is None:
        product.sold = 0
    product.sold += 1
    product.stock -= 1
    db.session.commit()
    return redirect(url_for('index'))




# 商品削除
@app.route('/delete/<int:id>', methods=['POST'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('index'))


# 在庫追加
@app.route('/add_stock/<int:id>', methods=['POST'])
def add_stock(id):
    product = Product.query.get_or_404(id)
    product.stock += 1  
    db.session.commit()
    return redirect(url_for('index'))

# 在庫削除
@app.route('/remove_stock/<int:id>', methods=['POST'])
def remove_stock(id):
    product = Product.query.get_or_404(id)
    if product.stock > 0:
        product.stock -= 1  
        db.session.commit()
    return redirect(url_for('index'))

# ABC分析の実行
@app.route('/abc_analysis')
def abc_analysis():
    products = Product.query.all()
    product_sales = []
    
    for product in products:
        sales = product.sold * product.price  
        product_sales.append({'product': product, 'sales': sales})
    
    # 売上金額の並べ替え
    sorted_sales = sorted(product_sales, key=lambda x: x['sales'], reverse=True)
    
    # 累積売上金額
    total_sales = sum([item['sales'] for item in sorted_sales])
    cumulative_sales = 0
    for item in sorted_sales:
        cumulative_sales += item['sales']
        item['cumulative_percentage'] = (cumulative_sales / total_sales) * 100

    # ABC分析
    for item in sorted_sales:
        if item['cumulative_percentage'] <= 80:
            item['class'] = 'A'
        elif item['cumulative_percentage'] <= 90:
            item['class'] = 'B'
        else:
            item['class'] = 'C'

    return render_template('abc_analysis.html', sorted_sales=sorted_sales)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

