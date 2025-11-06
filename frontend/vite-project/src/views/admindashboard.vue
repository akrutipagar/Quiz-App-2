<template>
  <div>
    <h1><b>ADMIN DASHBOARD</b></h1>
    <button @click="logout">Logout</button><br>
    <input
      type="text"
      v-model="searchQuery"
      placeholder="Search subjects..."
      class="search-box"
    />
  </div>
  <br>
<div>
    <form @submit.prevent="editSubjectId ? editsubject() : createsubject()">
      <input v-model="subject.name" placeholder="Subject Name" required />
      <input v-model="subject.description" placeholder="Description" />
      <button type="submit">{{ editSubjectId ? 'Update' : 'Create' }} Subject</button>
      <button v-if="editSubjectId" @click.prevent="cancelEditSubject">Cancel</button>
    </form>

    <p v-if="message">{{ message }}</p>

    
    <div v-for="s in allSubjects" :key="s.id" class="subject-block">
      <h3>
        Subject: {{ s.name }} Description:({{ s.description }})
        <button @click="editSubject(s)">Edit</button>
        <button @click="deleteSubject(s.id)">Delete</button>
      </h3>
      

      <div v-for="c in s.chapters" :key="c.id" class="chapter-block">
        <div v-if="editChapterId === c.id">
          <input v-model="chapters[s.id].name" placeholder="Chapter Title" />
          <input v-model="chapters[s.id].description" placeholder="Chapter Content" />
          <button @click="editchapter(c.id, s.id)">Update</button>
          <button @click="cancelEditChapter">Cancel</button>
        </div>
        <div v-else>
          <h4>
            Chapter: {{c.title}}
            <button @click="editChapter(s.id, c)">Edit</button>
            <button @click="deleteChapter(c.id)">Delete</button>
          </h4>
         
        </div>

        
        <div v-for="q in c.quizzes" :key="q.id" class="quiz-block">
          <div v-if="editQuizId === q.id">
            <input v-model="quizzes[c.id].name" placeholder="Quiz Title" />
            <input v-model="quizzes[c.id].description" placeholder="Description" />
            <input v-model="quizzes[c.id].date_of_quiz" type="date" />
            <input v-model="quizzes[c.id].time_duration" type="time" />
            <button @click="updateQuiz(q.id, c.id)">Edit</button>
            <button @click="cancelEditQuiz">Cancel</button>
          </div>
          <div v-else>
            <h5>
              Quiz: {{ q.title }}
              <button @click="editQuiz(c.id, q)">Edit</button>
              <button @click="deleteQuiz(q.id)">Delete</button>
            </h5>
            <p>{{ q.description }}</p>
          </div>

          
          <ol>
            <li v-for="ques in q.questions" :key="ques.id">
              <strong>{{ ques.question_statement }}</strong><br />
              A. {{ ques.option1 }} B. {{ ques.option2 }} C. {{ ques.option3 }} D. {{ ques.option4 }}<br />
              Correct: {{ ques.correct_option }}
              <button @click="seteditquestion(q.id, ques)">Edit</button>
              <button @click="deleteQuestion(ques.id)">Delete</button>
            </li>
          </ol>

        
          <form @submit.prevent="submitQuestion(q.id)">
            <input v-model="questions[q.id].question_statement" placeholder="Question" required />
            <input v-model="questions[q.id].option1" placeholder="Option 1" />
            <input v-model="questions[q.id].option2" placeholder="Option 2" />
            <input v-model="questions[q.id].option3" placeholder="Option 3" />
            <input v-model="questions[q.id].option4" placeholder="Option 4" />
            <input v-model="questions[q.id].correct_option" placeholder="Correct Option (1-4)" />
            <button type="submit">{{ questions[q.id].id ? 'Update' : 'Add' }} Question</button>
            <button v-if="questions[q.id].id" @click.prevent="cancelEditQuestion(q.id)">Cancel</button>
          </form>
        </div>

      
        <form @submit.prevent="createQuiz(c.id)">
          <input v-model="quizzes[c.id].name" placeholder="Quiz Title" required />
          <input v-model="quizzes[c.id].description" placeholder="Description" />
          <input v-model="quizzes[c.id].date_of_quiz" type="date" required />
          <input v-model="quizzes[c.id].time_duration" type="time" required />
          <button type="submit">Add Quiz</button>
        </form>
      </div>

      
      <form @submit.prevent="createchapter(s.id)">
        <input v-model="chapters[s.id].name" placeholder="Chapter Title" required />
        <input v-model="chapters[s.id].description" placeholder="Chapter Content" />
        <button type="submit">Add Chapter</button>
      </form>
    </div>
    
    <hr />

    
    <h3>All Users and Their Quiz Scores</h3>
    <table border="1">
      <thead>
        <tr>
          <th>User</th>
          <th>Quiz</th>
          <th>Correct</th>
          <th>Total</th>
          <th>Score %</th>
          <th>Timestamp</th>
        </tr>
      </thead>
      <tbody>
        <template v-for="user in users" :key="user.id">
          <tr v-if="user.scores.length" v-for="s in user.scores" :key="s.quiz_id + s.timestamp">
            <td>{{ user.username }}</td>
            <td>{{ s.quiz_title }}</td>
            <td>{{ s.correct_answers }}</td>
            <td>{{ s.total_questions }}</td>
            <td>{{ s.total_score }}%</td>
            <td>{{ s.timestamp }}</td>
          </tr>
          <tr v-else>
            <td>{{ user.username }}</td>
            <td colspan="5">No quiz attempts</td>
          </tr>
        </template>
      </tbody>
    </table>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'AdminDashboard',
  data() {
    return {
      subject: { name: '', description: '' },
      subjects: [],
      chapters: {},
      quizzes: {},
      questions: {},
      message: '',
      editSubjectId: null,
      editChapterId: null,
      editQuizId: null,
      users: [],
      searchQuery: ''
    };
  },
  computed: {
    allSubjects() {
      if (!this.searchQuery.trim()) return this.subjects;
      return this.subjects.filter(subject =>
        subject.name.toLowerCase().includes(this.searchQuery.toLowerCase())
      );
    }
  },
  mounted() {
    this.getsubjects();
    this.Usersscores();
  },
  methods: {
    async getsubjects() {
      try {
        const res = await axios.get('http://localhost:5000/subjects', { withCredentials: true });
        this.subjects = res.data.subjects;

        this.subjects.forEach(subject => {
          this.chapters[subject.id] = { name: '', description: '' };
          subject.chapters.forEach(ch => {
            this.quizzes[ch.id] = { name: '', description: '', date_of_quiz: '', time_duration: '' };
            ch.quizzes.forEach(qz => {
              this.questions[qz.id] = {
                question_statement: '',
                option1: '',
                option2: '',
                option3: '',
                option4: '',
                correct_option: ''
              };
            });
          });
        });
      } catch (err) {
        console.error('Failed to load subjects:', err);
      }
    },

  

    async createsubject() {
      try {
        const exists = this.subjects.find(s => s.name.trim().toLowerCase() === this.subject.name.trim().toLowerCase());
        if (exists) {
          this.message = 'Subject already exists!';
          return;
        }

        await axios.post('http://localhost:5000/admin/create_subjects', this.subject, { withCredentials: true });
        this.subject = { name: '', description: '' };
        this.message = 'Subject created successfully.';
        this.getsubjects();
      } catch (error) {
        if (error.response?.status === 409) {
          this.message = 'Subject already exists!';
        } else if (error.response?.status === 403) {
          this.message = 'Only admins can create subjects.';
        } else {
          this.message = 'Error creating subject.';
        }
        console.error('Failed:', error);
      }
    },

    async editsubject() {
      await axios.put(`http://localhost:5000/admin/update_subjects/${this.editSubjectId}`, this.subject, { withCredentials: true });
      this.cancelEditSubject();
      this.getsubjects();
    },

    editSubject(s) {
      this.subject = { ...s };
      this.editSubjectId = s.id;
    },

    cancelEditSubject() {
      this.editSubjectId = null;
      this.subject = { name: '', description: '' };
    },

    async deleteSubject(id) {
      await axios.delete(`http://localhost:5000/admin/delete_subjects/${id}`, { withCredentials: true });
      this.getsubjects();
    },

    async createchapter(subjectId) {
      await axios.post(`http://localhost:5000/admin/create_chapter/${subjectId}`, this.chapters[subjectId], { withCredentials: true });
      this.chapters[subjectId] = { name: '', description: '' };
      this.getsubjects();
    },

    async editchapter(chapterId, subjectId) {
      await axios.put(`http://localhost:5000/admin/update_chapters/${chapterId}`, this.chapters[subjectId], { withCredentials: true });
      this.cancelEditChapter();
      this.getsubjects();
    },

    editChapter(subjectId, chapter) {
      this.chapters[subjectId] = { name: chapter.name, description: chapter.description };
      this.editChapterId = chapter.id;
    },

    cancelEditChapter() {
      this.editChapterId = null;
    },

    async deleteChapter(id) {
      await axios.delete(`http://localhost:5000/admin/delete_chapters/${id}`, { withCredentials: true });
      this.getsubjects();
    },

    async createQuiz(chapterId) {
      await axios.post(`http://localhost:5000/admin/create_quiz/${chapterId}`, this.quizzes[chapterId], { withCredentials: true });
      this.quizzes[chapterId] = { name: '', description: '', date_of_quiz: '', time_duration: '' };
      this.getsubjects();
    },

    async updateQuiz(quizId, chapterId) {
      await axios.put(`http://localhost:5000/admin/update_quizzes/${quizId}`, this.quizzes[chapterId], { withCredentials: true });
      this.cancelEditQuiz();
      this.getsubjects();
    },

    editQuiz(chapterId, quiz) {
      this.quizzes[chapterId] = { ...quiz };
      this.editQuizId = quiz.id;
    },

    cancelEditQuiz() {
      this.editQuizId = null;
    },

    async deleteQuiz(id) {
      await axios.delete(`http://localhost:5000/admin/delete_quizzes/${id}`, { withCredentials: true });
      this.getsubjects();
    },

    async submitQuestion(quizId) {
      const data = this.questions[quizId];
      if (data.id) {
        await axios.put(`http://localhost:5000/admin/update_question/${data.id}`, data, { withCredentials: true });
      } else {
        await axios.post(`http://localhost:5000/admin/create_question/${quizId}`, data, { withCredentials: true });
      }
      this.questions[quizId] = {
        question_statement: '',
        option1: '',
        option2: '',
        option3: '',
        option4: '',
        correct_option: ''
      };
      this.getsubjects();
    },

    seteditquestion(quizId, question) {
      this.questions[quizId] = { ...question };
    },

    cancelEditQuestion(quizId) {
      this.questions[quizId] = {
        question_statement: '',
        option1: '',
        option2: '',
        option3: '',
        option4: '',
        correct_option: ''
      };
    },

    async deleteQuestion(id) {
      await axios.delete(`http://localhost:5000/admin/delete_questions/${id}`, { withCredentials: true });
      this.getsubjects();
    },
    async Usersscores() {
      try {
        const res = await axios.get('http://localhost:5000/admin/users/scores', { withCredentials: true });
        this.users = res.data.users;
      } catch (err) {
        console.error("Failed to fetch user scores", err);
      }
    },
    async logout() {
    axios.post("http://localhost:5000/logout", {}, { withCredentials: true })
      .then(() => {
        this.$router.push('/login'); 
      })
      .catch(err => {
        console.error('Logout failed', err);
      });
  }

  }
};
</script>
