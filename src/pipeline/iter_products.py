from collections.abc import Iterator

def iter_products(self, since_epoch: int | None = None) -> Iterator[dict]:
    page = 1
    is_done = False
    while page <= self.settings.max_page_per_run and not is_done :
        data = self._fetch_page(page)
        products = data['products']

        if products == []:
            is_done = True
            break

        for product in products:

            last_modified = product.get('last_modified_t')

            if since_epoch is not None and last_modified < since_epoch:
                is_done = True
                break
            yield product
        page+=1