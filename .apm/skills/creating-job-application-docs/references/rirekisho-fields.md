# Rirekisho fields

Standard fields for a Japanese résumé (rirekisho), based on the Ministry of Health, Labour and Welfare's 2021 sample form.

In the Required column, ◯ means required and △ means optional. Quoted Japanese text is the wording used on the generated form.

## 1. Header

| Field | Required | Example |
| --- | --- | --- |
| Document title | ◯ | `履歴書` |
| Date prepared | ◯ | May 10, 2026, using either the Gregorian or Japanese era calendar |

## 2. Personal information

| Field | Required | Notes |
| --- | --- | --- |
| Full name in kanji | ◯ | Separate family and given names with a space |
| Name reading (furigana) | ◯ | Use hiragana |
| Date of birth | ◯ | Use the Gregorian or Japanese era calendar and include the applicant's age |
| Gender | △ | Optional; the applicant may choose not to include it |
| Photo area | ◯ | Reserve 30 mm × 40 mm; the actual image may be left blank |
| Postal code | ◯ | `〒XXX-XXXX` |
| Current address | ◯ | Start with the prefecture |
| Address reading (furigana) | ◯ | Use hiragana |
| Phone number | ◯ | Landline or mobile |
| Email address | ◯ | |
| Alternative contact address | △ | Include only if different from the current address |

## 3. Education and employment history

List entries in chronological order, oldest first.

| Field | Example |
| --- | --- |
| Year | 2018, or Heisei 30 |
| Month | 4 |
| Entry | Enrolled in a department and faculty at a university |

Conventions:

- Education commonly starts with junior high school graduation.
- Put `以上` at the right edge of the final row to mark the end of the entries.
- Use separate education and employment sections.

## 4. Licenses and qualifications

| Field | Example |
| --- | --- |
| Month and year obtained | June 2022 |
| Qualification | Obtained a Class 1 ordinary driver's license |

## 5. Motivation, strengths, and interests

Provide multiline text areas. Depending on the form, these may be separate sections for:

- Reasons for applying
- Personal strengths
- Employment preferences
- Hobbies and special skills

Do not include commuting time, number of dependents, or marital status unless the employer requests them. These fields were removed from the Ministry's sample form.

## 6. Employment preferences

Include preferences such as work location, role, and salary.

---

## Layout guidelines

- Use **two A4 portrait sheets** by default, following the Ministry's sample layout. Put personal information, the photo, education, and employment on the first sheet. Put licenses, qualifications, motivation, and employment preferences on the second.
- Place the photo area at the **top right** of the first sheet, at 30 mm × 40 mm.
- Use a **wide table** with year, month, and entry columns for education and employment.
- Separate sections with ruled borders in the `japanese-formal` style.
- Use 10–10.5 pt body text.
- Use a line height of 1.5–1.7 em.

### Page capacity guidelines

Template tables have fixed row heights, so use row counts to check whether content fits. Count an entry that wraps onto a second line as two rows.

| Area | japanese-formal | modern-simple |
| --- | --- | --- |
| Education and employment on sheet 1 | 20 rows | 12 rows |
| Licenses and qualifications on sheet 2 | 14 rows | 12 rows |
| Combined continuation rows and qualifications when history continues on sheet 2 | 11 rows | 10 rows |
| Motivation and related text | About 600 Japanese characters | About 550 Japanese characters |
| Employment preferences | About 240 Japanese characters | About 180 Japanese characters |

- For `japanese-formal`, the row counts include the education and employment headings, the blank row between them, and the final `以上` row. For `modern-simple`, count the education and employment entries together.
- If the history does not fit on sheet 1, continue it in a matching table at the top of sheet 2. Use `学歴・職歴（続き）` as the heading, or an appropriate heading such as `職歴（続き）` for `modern-simple`.
- Longer motivation or preference text expands its section and reduces the number of rows that fit on sheet 2.
- These estimates assume A4. B5 sheets hold less content.

### Landscape spreads

When the user requests landscape orientation, arrange the two portrait sheets side by side as a spread. Use paper twice the size of one sheet: A3 landscape for A4 sheets, or JIS-B4 landscape for B5 sheets.

1. Set `@page size` to `A3 landscape`, or `JIS-B4 landscape` for B5.
2. Wrap both `.page` elements in `<div class="spread">`.
3. Add the following CSS:

```css
.spread {
  display: flex;
  width: 420mm;              /* Twice the sheet width; use 364mm for JIS-B4 */
  margin: 0 auto;
}

.spread > .page {
  margin: 0;
}

.spread > .page + .page {
  break-before: auto;        /* Keep the second sheet in the same spread */
}
```

Each sheet retains its portrait dimensions, so the page capacity guidelines still apply.

## Required information

Collect the following from the user:

1. Full name in kanji and furigana
2. Date of birth
3. Gender, including whether to show it
4. Address and contact details
5. Education, starting with junior high school graduation
6. Employment history
7. Qualifications and licenses
8. Reasons for applying
9. Personal strengths, hobbies, and special skills
10. Employment preferences
