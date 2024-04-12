interface ISiteMetadataResult {
  siteTitle: string;
  siteUrl: string;
  description: string;
  logo: string;
  navLinks: {
    name: string;
    url: string;
  }[];
}

const data: ISiteMetadataResult = {
  siteTitle: 'ArtsyLee跑步数据',
  siteUrl: 'https://www.artsylee.cn',
  logo: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQTtc69JxHNcmN1ETpMUX4dozAgAN6iPjWalQ&usqp=CAU',
  description: 'Personal site and blog',
  navLinks: [
    {
      name: '主页',
      url: 'https://www.artsylee.cn',
    },
    {
      name: '关于',
      url: 'https://github.com/ArtsyLee/running/tree/master',
    },
  ],
};

export default data;
