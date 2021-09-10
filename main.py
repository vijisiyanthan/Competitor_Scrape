from WebDriver import NellaOnlineCollectionsPage

if __name__ == '__main__':
    collection = input("Enter Collection Page: ")
    Nella_Collection_Page = NellaOnlineCollectionsPage()
    Nella_Collection_Page.scrape(collection_name=collection)
    # for a in Nella_Collection_Page.page_links:
    #     print(a)
    print(Nella_Collection_Page.df_products)
    Nella_Collection_Page.df_products.to_csv("Final.csv")