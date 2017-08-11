import crawler as main
import time

if __name__ == "__main__":
    start_time = time.time()
    main.set_accepted_domains(["www.malwarebytes.com","support.malwarebytes.com"])
    main.set_disallowed_domains([""])
    main.boot_db()
    main.get_redirects(recheck_redirects=True)
    # main.check_old()
    main.start_crawl("https://www.malwarebytes.com/sitemap.xml")
    print(main.find_code([404]))
    # print(main.crawl_only_this_page("https://www.malwarebytes.com/thank_you/", [404]))
    # print(main.find_link("https://www.malwarebytes.com/premium"))
    # print(main.find_code_of_url("https://www.malwarebytes.com/premium"))
    # print(main.search("inapp"))
    print("--- %s seconds ---" % (time.time() - start_time))
