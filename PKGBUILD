pkgname=unidesk
pkgver=1.0
pkgrel=1
pkgdesc="App for UniOS"
arch=('any')
url="https://github.com/open-source-uom/UniDesk"
license=('GPL3')
depends=('python' 'python-pyqt6')
makedepends=('python-build' 'python-installer' 'python-wheel' 'python-setuptools')
source=()
sha256sums=()

build() {
    cd "$startdir"
    python -m build --wheel --no-isolation
}

package() {
    cd "$startdir"
    python -m installer --destdir="$pkgdir" dist/*.whl

    install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}