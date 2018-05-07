class Theme:

    theme_actif = None
    theme_list = {}

    def __init__(self, major, medium, minor, m2, m3, l2, l3, reg):
        self.major = major
        self.medium = medium
        self.minor = minor
        self.m2 = m2
        self.m3 = m3
        self.l2 = l2
        self.l3 = l3
        self.reg = reg


Theme.theme_list.update({'Université Laval': Theme('#E30513', '#FFC103', '#00AFEC',
                                                   '#ffaccb', '#ff0000', '#00c9ff', '#0051ff', '#f5ebdc')})
Theme.theme_list.update({'Université Laval - Inversé': Theme('#FFC103', '#E30513', '#00AFEC',
                                                             '#ffaccb', '#ff0000', '#00c9ff', '#0051ff', '#f5ebdc')})
Theme.theme_list.update({'Dracula': Theme('#2B2B2B', '#629755', '#9876AA',
                                          '#CC7832', '#BBB529', '#79ABFF', '#D8D8D8', '#424445')})

Theme.theme_actif = Theme.theme_list['Université Laval - Inversé']