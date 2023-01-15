"use strict";

const notesListElement = document.querySelector(".notes-list");
const loader = document.querySelector('.loader');
const notesAddForm = document.querySelector('.notes-add-form');


async function addNote(author, title, content) {
    let response = await fetch(`https://d5daumt9fs4pt6chqv6p.apigw.yandexcloud.net/notes`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({author: author, text: content, title: title})
    });
    let result = await response.json();

    return result;
}

function submitNotesAddFormHandler(e) {
    e.preventDefault();
    const form = e.target;
    const formFields = form.elements;
    const fieldsToClear = [formFields.author, formFields.title, formFields.text];
    const author = formFields.author.value;
    const title = formFields.title.value;
    const content = formFields.text.value;

    addNote(author, title, content)
        .then((note) => {
            let noteItem = createNoteItem(note.author,  note.title, note.text, note.created_at);
            notesListElement.appendChild(noteItem);
            fieldsToClear.forEach(field => {
                field.value = "";
            })
        })
}

notesAddForm.addEventListener("submit", submitNotesAddFormHandler);


function createNoteItem(author, title, text, createdAt){
    let container = document.createElement('li');
    let titleEl = document.createElement('h2');
    let authorEl = document.createElement('p');
    let textEl = document.createElement('p');
    let createdAtEl = document.createElement('i');


    container.classList.add("notes-item");
    titleEl.textContent = title;
    textEl.textContent = text;
    authorEl.textContent = author;
    createdAtEl.textContent = createdAt;

    container.appendChild(titleEl);
    container.appendChild(authorEl);
    container.appendChild(textEl);
    container.appendChild(createdAtEl);

    return container;
};

async function initNotesList() {
    let response = await fetch(`https://d5daumt9fs4pt6chqv6p.apigw.yandexcloud.net/notes`, {
        method: 'GET'
    });
    let result = await response.json();

    return result;
}

initNotesList().then((res) => {
    res.sort((note1, note2) => new Date(note1.created_at) - new Date(note2.created_at));

    res.forEach(note => {
        let noteItem = createNoteItem(note.author, note.title, note.text, note.created_at);
        notesListElement.appendChild(noteItem);
    });
});