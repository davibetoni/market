Rails.application.routes.draw do
  root 'homepage#index'
  post 'homepage/info', to: 'homepage#info', as: 'homepage_info'

  get 'up' => 'rails/health#show', as: :rails_health_check
end
