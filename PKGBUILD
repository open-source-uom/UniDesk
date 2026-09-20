pkgname=unidesk
pkgver=1.0
pkgrel=1
pkgdesc="Welcome and academic configuration app for UniOS"
arch=('any')
url="https://github.com/opensource-uom/unidesk"
license=('GPL-3.0-or-later')
depends=(
    'python'
    'python-pyqt6'
)
makedepends=(
    'python-build'
    'python-installer'
    'python-wheel'
    'python-setuptools'
)
source=()
sha256sums=()

build() {
    cd "$startdir"
    python -m build --wheel --no-isolation
}

package() {
    cd "$startdir"

    python -m installer --destdir="$pkgdir" dist/*.whl

    install -Dm644 "$startdir/resources/unidesk.desktop" \
        "$pkgdir/usr/share/applications/unidesk.desktop"

    if [ -f "$startdir/resources/unios.png" ]; then
        install -Dm644 "$startdir/resources/unios.png" \
            "$pkgdir/usr/share/pixmaps/unidesk.png"
        install -Dm644 "$startdir/resources/unios.png" \
            "$pkgdir/usr/share/icons/hicolor/128x128/apps/unidesk.png"
    else
        echo "==> WARNING: resources/unios.png not found in $startdir"
        sed -i 's/^Icon=unidesk$/Icon=system-help/' \
            "$pkgdir/usr/share/applications/unidesk.desktop"
    fi

    install -Dm644 "$pkgdir/usr/share/applications/unidesk.desktop" \
        "$pkgdir/etc/xdg/autostart/unidesk.desktop"
}