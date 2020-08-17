
class trade:
    fund = 10000 * 1000  # W
    fund_lock = 0
    hold_up = 0
    hold_dn = 0

    def __init__(self, initials=0):
        if initials > 0:
            self.fund = initials

    def get_max_holds(self, price):
        return int(self.fund / price / 100)

    def open_up(self, at_price, holds, ds=''):
        self.open('UP', at_price, holds, ds)

    def open(self, direction, at_price, holds, ds=''):
        spend = at_price * holds * 100

        if direction == 'UP':
            if spend > self.fund:
                spend = self.fund
                holds = spend / at_price

            self.fund -= spend
            self.hold_up += holds

            op = '%s OPEN UP %.2f X %dS->' % (ds, at_price, holds)
            self.show_detail(at_price, indent=2, insert=op)

        elif direction == 'DN':
            self.fund_lock += spend
            self.hold_dn += holds

            op = '%s OPEN DN %.2f X %dS ->' % (ds, at_price, holds)
            self.show_detail(0, at_price, indent=2, insert=op)

    def close_up(self, at_price, holds=-1, ds=''):
        self.close_up('UP', at_price, holds)

    def close(self, direction, at_price, holds=-1, ds=''):
        if direction == 'UP':
            if self.hold_up < holds:
                holds = self.hold_up
            if holds == -1:
                holds = self.hold_up
            if holds == 0:
                return
            self.fund += at_price * holds * 100
            self.hold_up -= holds

            op = '%s CLOSE UP %.2f X %dS ->' % (ds, at_price, holds)
            self.show_detail(indent=2, insert=op)

        elif direction == 'DN':
            if holds > self.hold_dn:
                holds = self.hold_dn
            if holds == -1:
                holds = self.hold_dn

            if holds == 0:
                return
            spend = at_price * holds * 100
            self.fund_lock -= spend
            self.fund += self.fund_lock
            self.fund_lock = 0
            self.hold_dn -= holds

            op = '%s CLOSE DN %.2f X %dS ->' % (ds, at_price, holds)
            self.show_detail(indent=2, insert=op)

    def show_detail(self, up_price=0, dn_price=0, indent=0, insert=''):
        W = 10000
        ind = ''
        if indent > 0:
            ind = (' ' * indent)

        print("-------------------")
        if insert != '':
            print(insert)

        fund = self.fund / W
        fund_L = self.fund_lock / W
        hold_up_fund = (self.hold_up * 100 * up_price) / W
        hold_dn_fund = (self.hold_dn * 100 * dn_price) / W
        dn_earn = fund_L - hold_dn_fund

        print("%s cash valid : %.2f" % (ind, fund))
        if hold_up_fund > 0 : print("%s fund hold  : %.2fW" % (ind, hold_up_fund))
        if fund_L > 0 : print("%s fund lock  : %.2f -> %.2f (%.2f)W" % (ind, fund_L, hold_dn_fund, dn_earn))
        print("%s fund total : %.2fW" % (ind, fund + hold_up_fund + dn_earn))
        if self.hold_up > 0 : print("%s open UP    : %.2f X %dS" % (ind, up_price, self.hold_up))
        if self.hold_dn > 0 : print("%s open DN    : %.2f X %dS" % (ind, dn_price, self.hold_dn))

    def get_fund_tital(self, up_price, dn_price):
        W = 10000
        fund = self.fund / W
        fund_L = self.fund_lock / W
        hold_up_fund = (self.hold_up * 100 * up_price) / W
        hold_dn_fund = (self.hold_dn * 100 * dn_price) / W
        dn_earn = fund_L - hold_dn_fund
        return fund + hold_up_fund + dn_earn

    def show_total(self, up_price=0, dn_price=0):
        print("fund total : %.2f W" % self.get_fund_tital(up_price, dn_price))


if __name__ == '__main__':
    td = trade()

    td.show_detail()
    td.open('UP', 10000, 1)
    td.show_detail(11000)
    td.show_detail(12000)
    td.close('UP', 12000, 1)

    td.open('DN', 10000, 1)
    td.show_detail(0, 9500)
    td.show_detail(0, 9000)
    td.close('DN', 9000, 1)

    td.open('DN', 10000, 1)
    td.show_detail(0, 11000)
    td.show_detail(0, 12000)
    td.close('DN', 13000, 1)
