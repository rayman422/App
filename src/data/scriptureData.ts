import { Scripture, CrossReference } from '../types';

// Cross-reference helper function
const createCrossRef = (
  volume: 'ot' | 'nt' | 'bom' | 'dc' | 'pogp',
  book: string,
  chapter: number,
  verse: number,
  text: string,
  label: string
): CrossReference => ({
  id: `${volume}-${book.toLowerCase().replace(/\s+/g, '-')}-${chapter}-${verse}`,
  volume,
  book,
  chapter,
  verse,
  text,
  label
});

export const scriptureData: Scripture = {
  volumes: [
    {
      id: 'bom',
      name: 'Book of Mormon',
      abbreviation: 'BofM',
      books: [
        {
          id: '1-nephi',
          name: '1 Nephi',
          fullName: 'The First Book of Nephi',
          abbreviation: '1 Ne.',
          chapters: [
            {
              id: '1-nephi-1',
              book: '1 Nephi',
              chapter: 1,
              title: 'Nephi begins his record—Lehi sees a vision of the tree of life and reads from a book of prophecy—He prophesies the coming of the Lamb of God—He is persecuted by the Jews.',
              summary: 'Nephi introduces his record and tells of his father Lehi\'s vision and prophecies.',
              verses: [
                {
                  id: '1-nephi-1-1',
                  book: '1 Nephi',
                  chapter: 1,
                  verse: 1,
                  text: 'I, Nephi, having been born of goodly parents, therefore I was taught somewhat in all the learning of my father; and having seen many afflictions in the course of my days, nevertheless, having been highly favored of the Lord in all my days; yea, having had a great knowledge of the goodness and the mysteries of God, therefore I make a record of my proceedings in my days.',
                  crossReferences: [
                    createCrossRef('bom', '2 Nephi', 4, 15, 'And upon these I write the things of my soul', '2 Ne. 4:15'),
                    createCrossRef('dc', 'D&C', 18, 10, 'Remember the worth of souls is great in the sight of God', 'D&C 18:10')
                  ],
                  topicalGuideEntries: ['Record Keeping', 'Learning', 'Goodly Parents']
                },
                {
                  id: '1-nephi-1-2',
                  book: '1 Nephi',
                  chapter: 1,
                  verse: 2,
                  text: 'Yea, I make a record in the language of my father, which consists of the learning of the Jews and the language of the Egyptians.',
                  crossReferences: [
                    createCrossRef('bom', 'Mormon', 9, 32, 'And now, behold, we have written this record according to our knowledge, in the characters which are called among us the reformed Egyptian', 'Morm. 9:32')
                  ],
                  topicalGuideEntries: ['Language', 'Record Keeping', 'Learning']
                },
                {
                  id: '1-nephi-1-3',
                  book: '1 Nephi',
                  chapter: 1,
                  verse: 3,
                  text: 'And I know that the record which I make is true; and I make it with mine own hand; and I make it according to my knowledge.',
                  crossReferences: [
                    createCrossRef('bom', 'Jacob', 1, 4, 'And if there were preaching which was sacred, or revelation which was great, or prophesying, that I should engraven the heads of them upon these plates', 'Jacob 1:4'),
                    createCrossRef('dc', 'D&C', 1, 24, 'Behold, I am God and have spoken it; these commandments are of me', 'D&C 1:24')
                  ],
                  topicalGuideEntries: ['Truth', 'Testimony', 'Record Keeping']
                }
              ]
            },
            {
              id: '1-nephi-3',
              book: '1 Nephi',
              chapter: 3,
              title: 'Lehi\'s sons return to Jerusalem to obtain the plates of brass—Laban refuses to give the plates up—Nephi exhorts and encourages his brethren—Laban takes their property and attempts to slay them—Laman and Lemuel smite Nephi and Sam and are reproved by an angel.',
              summary: 'Nephi and his brothers are commanded to obtain the brass plates from Laban.',
              verses: [
                {
                  id: '1-nephi-3-7',
                  book: '1 Nephi',
                  chapter: 3,
                  verse: 7,
                  text: 'And it came to pass that I, Nephi, said unto my father: I will go and do the things which the Lord hath commanded, for I know that the Lord giveth no commandments unto the children of men, save he shall prepare a way for them that they may accomplish the thing which he commandeth them.',
                  crossReferences: [
                    createCrossRef('ot', '1 Kings', 8, 56, 'There hath not failed one word of all his good promise', '1 Kgs. 8:56'),
                    createCrossRef('dc', 'D&C', 82, 10, 'I, the Lord, am bound when ye do what I say; but when ye do not what I say, ye have no promise', 'D&C 82:10'),
                    createCrossRef('bom', '1 Nephi', 17, 3, 'And thus we see that the commandments of God must be fulfilled', '1 Ne. 17:3')
                  ],
                  topicalGuideEntries: ['Obedience', 'Faith', 'God\'s Promises', 'Trust in the Lord']
                }
              ]
            }
          ]
        },
        {
          id: '2-nephi',
          name: '2 Nephi',
          fullName: 'The Second Book of Nephi',
          abbreviation: '2 Ne.',
          chapters: [
            {
              id: '2-nephi-2',
              book: '2 Nephi',
              chapter: 2,
              title: 'Redemption comes through the Holy Messiah—Freedom of choice (agency) is essential to existence and progression—Adam fell that men might be—Men are free to choose liberty and eternal life.',
              summary: 'Lehi teaches about the fall, redemption, and agency.',
              verses: [
                {
                  id: '2-nephi-2-25',
                  book: '2 Nephi',
                  chapter: 2,
                  verse: 25,
                  text: 'Adam fell that men might be; and men are, that they might have joy.',
                  crossReferences: [
                    createCrossRef('ot', 'Genesis', 3, 6, 'And when the woman saw that the tree was good for food', 'Gen. 3:6'),
                    createCrossRef('nt', 'Romans', 5, 12, 'Wherefore, as by one man sin entered into the world', 'Rom. 5:12'),
                    createCrossRef('dc', 'D&C', 93, 33, 'For man is spirit. The elements are eternal', 'D&C 93:33'),
                    createCrossRef('bom', 'Alma', 42, 8, 'Now behold, it was not expedient that man should be reclaimed from this temporal death', 'Alma 42:8')
                  ],
                  topicalGuideEntries: ['Fall of Adam', 'Joy', 'Plan of Salvation', 'Purpose of Life']
                }
              ]
            }
          ]
        },
        {
          id: 'mosiah',
          name: 'Mosiah',
          fullName: 'The Book of Mosiah',
          abbreviation: 'Mosiah',
          chapters: [
            {
              id: 'mosiah-2',
              book: 'Mosiah',
              chapter: 2,
              title: 'King Benjamin addresses his people—He recounts the equity, fairness, and spirituality of his reign—He counsels them to serve their heavenly King—Those who rebel against God shall suffer anguish like unquenchable fire.',
              summary: 'King Benjamin teaches about service and our debt to God.',
              verses: [
                {
                  id: 'mosiah-2-17',
                  book: 'Mosiah',
                  chapter: 2,
                  verse: 17,
                  text: 'And behold, I tell you these things that ye may learn wisdom; that ye may learn that when ye are in the service of your fellow beings ye are only in the service of your God.',
                  crossReferences: [
                    createCrossRef('nt', 'Matthew', 25, 40, 'Inasmuch as ye have done it unto one of the least of these my brethren, ye have done it unto me', 'Matt. 25:40'),
                    createCrossRef('dc', 'D&C', 42, 29, 'If thou lovest me thou shalt serve me and keep all my commandments', 'D&C 42:29'),
                    createCrossRef('bom', 'Alma', 34, 28, 'And now behold, my beloved brethren, I say unto you, do not suppose that this is all', 'Alma 34:28')
                  ],
                  topicalGuideEntries: ['Service', 'Love of God', 'Charity', 'Fellow Beings']
                }
              ]
            }
          ]
        },
        {
          id: 'alma',
          name: 'Alma',
          fullName: 'The Book of Alma',
          abbreviation: 'Alma',
          chapters: [
            {
              id: 'alma-32',
              book: 'Alma',
              chapter: 32,
              title: 'Alma teaches the poor whose afflictions had humbled them—Faith is a hope in that which is not seen which is true—Alma testifies that the word is good.',
              summary: 'Alma teaches about faith and how to nurture it.',
              verses: [
                {
                  id: 'alma-32-21',
                  book: 'Alma',
                  chapter: 32,
                  verse: 21,
                  text: 'And now as I said concerning faith—faith is not to have a perfect knowledge of things; therefore if ye have faith ye hope for things which are not seen, which are true.',
                  crossReferences: [
                    createCrossRef('nt', 'Hebrews', 11, 1, 'Now faith is the substance of things hoped for, the evidence of things not seen', 'Heb. 11:1'),
                    createCrossRef('bom', 'Ether', 12, 6, 'And now, I, Moroni, would speak somewhat concerning these things', 'Ether 12:6'),
                    createCrossRef('dc', 'D&C', 46, 14, 'To another it is given to believe on their words', 'D&C 46:14')
                  ],
                  topicalGuideEntries: ['Faith', 'Hope', 'Knowledge', 'Testimony']
                }
              ]
            }
          ]
        },
        {
          id: 'moroni',
          name: 'Moroni',
          fullName: 'The Book of Moroni',
          abbreviation: 'Moro.',
          chapters: [
            {
              id: 'moroni-10',
              book: 'Moroni',
              chapter: 10,
              title: 'A testimony of the Book of Mormon comes by the power of the Holy Ghost—The gifts of the Spirit are dispensed to the faithful—Spiritual gifts always accompany faith—Moroni\'s words speak from the dust—Come unto Christ, be perfected in Him, and sanctify your souls.',
              summary: 'Moroni\'s promise about receiving a testimony of the Book of Mormon.',
              verses: [
                {
                  id: 'moroni-10-4',
                  book: 'Moroni',
                  chapter: 10,
                  verse: 4,
                  text: 'And when ye shall receive these things, I would exhort you that ye would ask God, the Eternal Father, in the name of Christ, if these things are not true; and if ye shall ask with a sincere heart, with real intent, having faith in Christ, he will manifest the truth of it unto you, by the power of the Holy Ghost.',
                  crossReferences: [
                    createCrossRef('nt', 'James', 1, 5, 'If any of you lack wisdom, let him ask of God', 'James 1:5'),
                    createCrossRef('dc', 'D&C', 9, 8, 'But, behold, I say unto you, that you must study it out in your mind', 'D&C 9:8'),
                    createCrossRef('bom', 'Alma', 5, 45, 'And this is not all. Do ye not suppose that I know of these things myself?', 'Alma 5:45')
                  ],
                  topicalGuideEntries: ['Prayer', 'Holy Ghost', 'Testimony', 'Truth']
                },
                {
                  id: 'moroni-10-5',
                  book: 'Moroni',
                  chapter: 10,
                  verse: 5,
                  text: 'And by the power of the Holy Ghost ye may know the truth of all things.',
                  crossReferences: [
                    createCrossRef('nt', 'John', 16, 13, 'Howbeit when he, the Spirit of truth, is come, he will guide you into all truth', 'John 16:13'),
                    createCrossRef('dc', 'D&C', 35, 19, 'For I will reveal unto them, even as unto Moses', 'D&C 35:19')
                  ],
                  topicalGuideEntries: ['Holy Ghost', 'Truth', 'Revelation', 'Knowledge']
                }
              ]
            }
          ]
        }
      ]
    },
    {
      id: 'dc',
      name: 'Doctrine and Covenants',
      abbreviation: 'D&C',
      books: [
        {
          id: 'dc',
          name: 'D&C',
          fullName: 'Doctrine and Covenants',
          abbreviation: 'D&C',
          chapters: [
            {
              id: 'dc-1',
              book: 'D&C',
              chapter: 1,
              title: 'The Lord\'s Preface to the Doctrine and Covenants',
              summary: 'The Lord\'s voice of warning to all people.',
              verses: [
                {
                  id: 'dc-1-38',
                  book: 'D&C',
                  chapter: 1,
                  verse: 38,
                  text: 'What I the Lord have spoken, I have spoken, and I excuse not myself; and though the heavens and the earth pass away, my word shall not pass away, but shall all be fulfilled, whether by mine own voice or by the voice of my servants, it is the same.',
                  crossReferences: [
                    createCrossRef('nt', 'Matthew', 24, 35, 'Heaven and earth shall pass away, but my words shall not pass away', 'Matt. 24:35'),
                    createCrossRef('bom', '2 Nephi', 9, 16, 'For behold, can flesh inherit the kingdom of God?', '2 Ne. 9:16')
                  ],
                  topicalGuideEntries: ['Word of God', 'Revelation', 'Prophets']
                }
              ]
            },
            {
              id: 'dc-6',
              book: 'D&C',
              chapter: 6,
              title: 'Revelation given to Joseph Smith the Prophet and Oliver Cowdery',
              summary: 'The work of God and how to approach it.',
              verses: [
                {
                  id: 'dc-6-36',
                  book: 'D&C',
                  chapter: 6,
                  verse: 36,
                  text: 'Look unto me in every thought; doubt not, fear not.',
                  crossReferences: [
                    createCrossRef('bom', 'Alma', 37, 36, 'Yea, and cry unto God for all thy support', 'Alma 37:36'),
                    createCrossRef('nt', 'Philippians', 4, 6, 'Be careful for nothing; but in every thing by prayer', 'Philip. 4:6')
                  ],
                  topicalGuideEntries: ['Trust in the Lord', 'Fear', 'Doubt', 'Faith']
                }
              ]
            },
            {
              id: 'dc-82',
              book: 'D&C',
              chapter: 82,
              title: 'Revelation given through Joseph Smith the Prophet',
              summary: 'Instructions about accountability and divine promises.',
              verses: [
                {
                  id: 'dc-82-10',
                  book: 'D&C',
                  chapter: 82,
                  verse: 10,
                  text: 'I, the Lord, am bound when ye do what I say; but when ye do not what I say, ye have no promise.',
                  crossReferences: [
                    createCrossRef('bom', '1 Nephi', 3, 7, 'And it came to pass that I, Nephi, said unto my father: I will go and do', '1 Ne. 3:7'),
                    createCrossRef('ot', 'Joshua', 1, 8, 'This book of the law shall not depart out of thy mouth', 'Josh. 1:8')
                  ],
                  topicalGuideEntries: ['Obedience', 'Promises', 'Accountability', 'Covenants']
                }
              ]
            },
            {
              id: 'dc-121',
              book: 'D&C',
              chapter: 121,
              title: 'The prayer and prophecies of Joseph Smith the Prophet',
              summary: 'Joseph Smith\'s prayer from Liberty Jail and the Lord\'s response.',
              verses: [
                {
                  id: 'dc-121-7',
                  book: 'D&C',
                  chapter: 121,
                  verse: 7,
                  text: 'My son, peace be unto thy soul; thine adversity and thine afflictions shall be but a small moment;',
                  crossReferences: [
                    createCrossRef('nt', '2 Corinthians', 4, 17, 'For our light affliction, which is but for a moment', '2 Cor. 4:17'),
                    createCrossRef('bom', 'Alma', 36, 3, 'And now, O my son Helaman, behold, thou art in thy youth', 'Alma 36:3')
                  ],
                  topicalGuideEntries: ['Adversity', 'Peace', 'Comfort', 'Affliction']
                },
                {
                  id: 'dc-121-45',
                  book: 'D&C',
                  chapter: 121,
                  verse: 45,
                  text: 'Let thy bowels also be full of charity towards all men, and to the household of faith, and let virtue garnish thy thoughts unceasingly; then shall thy confidence wax strong in the presence of God; and the doctrine of the priesthood shall distil upon thy soul as the dews from heaven.',
                  crossReferences: [
                    createCrossRef('nt', '1 Corinthians', 13, 4, 'Charity suffereth long, and is kind', '1 Cor. 13:4'),
                    createCrossRef('bom', 'Moroni', 7, 47, 'But charity is the pure love of Christ', 'Moro. 7:47')
                  ],
                  topicalGuideEntries: ['Charity', 'Virtue', 'Confidence', 'Priesthood']
                }
              ]
            }
          ]
        }
      ]
    }
  ]
};