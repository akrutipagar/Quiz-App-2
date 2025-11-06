<template>
  <div class="user-dashboard">
    <h2>Welcome!</h2>
     <button @click="logout">Logout</button><br>
   
    <div v-for="subject in subjects" :key="subject.id" class="subject-block">
      <h3>Subject:{{ subject.name }}</h3>
      <p>Subject Description:{{ subject.description }}</p>

      <div v-for="chapter in subject.chapters" :key="chapter.id" class="chapter-block">
        <h4>Chapter:{{ chapter.title }}</h4>
        <p>Chapter Description:{{ chapter.content }}</p>

        <div v-for="quiz in chapter.quizzes" :key="quiz.id" class="quiz-block">
          <h5>Quiz :{{ quiz.title }} - {{ quiz.date_of_quiz }}</h5>
          <p>Quiz Description:{{ quiz.description }}</p>
            <p> (Duration: {{ quiz.time_duration }})</p>
          <button @click="startQuiz(quiz)">Attempt Quiz</button>
        </div>
      </div>
    </div>
    <div v-if="activeQuiz" class="quiz-attempt">
      <h3>Attempting Quiz: {{ activeQuiz.title }}</h3>
      <p>Remaining Time: {{ minutes }}:{{ seconds < 10 ? '0' + seconds : seconds }}</p>
      <form @submit.prevent="submitQuiz">
        <div v-for="question in activeQuiz.questions" :key="question.id">
          <p>{{ question.question_statement }}</p>
          <div v-for="(option, index) in getOptions(question)" :key="index">
            <label>
              <input
                type="radio"
                :name="'question-' + question.id"
                :value="option"
                v-model="answers[question.id]"
                :disabled="showFeedback"
              />
              {{ option }}
            </label>
          </div>
          <div v-if="showFeedback && correctAnswer[question.id]">
            <p v-if="answers[question.id] === correctAnswer[question.id]">
              Correct Answer!
            </p>
            <p v-else>
               Your Answer: {{ answers[question.id] }}<br />
               Correct Answer: {{ correctAnswer[question.id] }}
            </p>
          </div>
        </div>
        <button type="submit" :disabled="showFeedback">Submit</button>
        <button @click.prevent="cancelQuiz">Cancel</button>
      </form>
    </div>

    
    <div v-if="score !== null">
      <h4>Quiz Submitted</h4>
      <p>Total Questions: {{ total }}</p>
      <p>Correct: {{ correct }}</p>
      <p>Score: {{ score }}%</p>
    </div>

    <h3> Monthly Activity Report</h3>
    <div v-if="monthlyReport.length > 0">
      <p>Total Quizzes Attempted: {{ totalQuizzes }}</p>
      

      <table border="1" >
        <thead>
          <tr>
            <th>Quiz Title</th>
            <th>Date</th>
            <th>Score</th>
            
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in monthlyReport" :key="item.quiz_title + item.date">
            <td>{{ item.quiz_title }}</td>
            <td>{{ item.date }}</td>
            <td>{{ item.score }}%</td>
            
          </tr>
        </tbody>
      </table>
    </div>
    <div v-else>
      <p>No activity this month.</p>
    </div>

    
    <div>
      <button @click="triggerExport">Export Quiz Results</button>
      <p v-if="message">{{ message }}</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      subjects: [],
      activeQuiz: null,
      answers: {},
      score: null,
      correct: 0,
      total: 0,
      minutes: 0,
      seconds: 0,
      timer: null,
      reminders: [],
      monthlyReport: [],
      avgScore: 0,
      totalQuizzes: 0,
      message: '',
      showFeedback: false,
      correctAnswer: {}
    };
  },
  methods: {
    getOptions(q) {
      return [q.option1, q.option2, q.option3, q.option4].filter(Boolean);
    },
    async fetchSubjects() {
      const res = await axios.get('http://localhost:5000/subjects', { withCredentials: true });
      this.subjects = res.data.subjects;
    },
    async fetchMonthlyReport() {
      const res = await axios.get('http://localhost:5000/user/monthly-report', { withCredentials: true });
      if (res.data.report) {
        this.monthlyReport = res.data.report;
        this.avgScore = res.data.avg_score;
        this.totalQuizzes = res.data.total_quizzes;
      }
    },
    startQuiz(quiz) {
      this.activeQuiz = quiz;
      this.answers = {};
      this.score = null;
      this.correct = 0;
      this.total = 0;
      this.showFeedback = false;

      const [hh, mm, ss] = this.activeQuiz.time_duration.split(":");
      this.minutes = parseInt(mm);
      this.seconds = parseInt(ss);
      this.startTimer();
    },
    startTimer() {
      this.timer = setInterval(() => {
        if (this.minutes === 0 && this.seconds === 0) {
          clearInterval(this.timer);
          alert(" Time's up! Submitting the quiz automatically.");
          this.submitQuiz();
          return;
        }
        if (this.seconds === 0) {
          this.minutes--;
          this.seconds = 59;
        } else {
          this.seconds--;
        }
      }, 1000);
    },
    cancelQuiz() {
      clearInterval(this.timer);
      this.activeQuiz = null;
      this.answers = {};
      this.score = null;
    },
    async submitQuiz() {
      clearInterval(this.timer);
      try {
        const res = await axios.post(
          `http://localhost:5000/user/submit_quiz/${this.activeQuiz.id}`,
          { answers: this.answers },
          { withCredentials: true }
        );
        this.score = res.data.score;
        this.correct = res.data.correct;
        this.total_questions = res.data.total_questions;
        this.correctAnswer = res.data.correct_answers;
        this.showFeedback = true;
      } catch (err) {
        console.error('Quiz submission failed');
        alert("Failed to submit quiz.");
      }
    },
    async logout() {
    axios.post("http://localhost:5000/logout", {}, { withCredentials: true })
      .then(() => {
        this.$router.push('/login');  // or window.location.href = '/login';
      })
      .catch(err => {
        console.error('Logout failed', err);
      });
  },
  
  triggerExport() {
  axios.get("http://localhost:5000/user/monthly-report", {
    withCredentials: true,
    responseType: 'blob' //
  })
  .then((res) => {
    const blob = new Blob([res.data], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'monthly_report.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link); 
  })
  .catch(err => {
    console.error(err);
    alert("Failed to export CSV");
  });
}
},
 mounted() {
    this.fetchSubjects();
    this.fetchMonthlyReport();
  }


 
};
</script>


